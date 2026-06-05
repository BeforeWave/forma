#!/usr/bin/env python3
"""Load GitHub issue body and comments for planning context."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from typing import Any


ISSUE_URL_RE = re.compile(
    r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/issues/[0-9]+(?:[?#][^\s<>'\"]*)?"
)
GITHUB_URL_RE = re.compile(r"https://github\.com/[^\s<>'\"]+")
JSON_FIELDS = (
    "number,title,body,state,labels,assignees,author,createdAt,updatedAt,url,comments"
)


def clean_url(raw: str) -> str:
    return raw.rstrip(").,;]")


def extract_issue_urls(text: str) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for match in ISSUE_URL_RE.finditer(text):
        url = clean_url(match.group(0))
        if url not in seen:
            urls.append(url)
            seen.add(url)
    return urls


def extract_unsupported_github_urls(text: str, issue_urls: list[str]) -> list[str]:
    supported = set(issue_urls)
    unsupported: list[str] = []
    seen: set[str] = set()
    for match in GITHUB_URL_RE.finditer(text):
        url = clean_url(match.group(0))
        if url in supported or "/issues/" in url:
            continue
        if url not in seen:
            unsupported.append(url)
            seen.add(url)
    return unsupported


def person_login(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("login") or value.get("name") or "")
    return str(value or "")


def names(values: Any) -> str:
    if not isinstance(values, list) or not values:
        return "-"
    rendered = []
    for item in values:
        if isinstance(item, dict):
            rendered.append(str(item.get("name") or item.get("login") or item))
        else:
            rendered.append(str(item))
    return ", ".join(rendered) if rendered else "-"


def run_gh(url: str) -> dict[str, Any]:
    command = ["gh", "issue", "view", url, "--json", JSON_FIELDS]
    result = subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "gh issue view failed")
    return json.loads(result.stdout)


def render_issue(data: dict[str, Any]) -> str:
    lines = [
        "# GitHub Issue Context",
        "",
        f"URL: {data.get('url', '-')}",
        f"Issue: #{data.get('number', '-')}",
        f"Title: {data.get('title', '-')}",
        f"State: {data.get('state', '-')}",
        f"Author: {person_login(data.get('author')) or '-'}",
        f"Labels: {names(data.get('labels'))}",
        f"Assignees: {names(data.get('assignees'))}",
        f"Created: {data.get('createdAt', '-')}",
        f"Updated: {data.get('updatedAt', '-')}",
        "",
        "## Body",
        "",
        str(data.get("body") or "").strip() or "(empty)",
        "",
        "## Comments",
        "",
    ]
    comments = data.get("comments") or []
    if not comments:
        lines.append("(no comments)")
    for index, comment in enumerate(comments, start=1):
        author = person_login(comment.get("author")) if isinstance(comment, dict) else "-"
        created = comment.get("createdAt", "-") if isinstance(comment, dict) else "-"
        body = comment.get("body", "") if isinstance(comment, dict) else str(comment)
        lines.extend(
            [
                f"### Comment {index} - {author or '-'} - {created}",
                "",
                str(body).strip() or "(empty)",
                "",
            ]
        )
    lines.extend(
        [
            "",
            "## Context Notes",
            "",
            "- Comments are chronological and part of the planning context.",
            "- Later comments may supersede the issue body or earlier comments.",
            "- If issue body and comments conflict, ask the user which version is authoritative.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_blocked(message: str) -> str:
    return (
        "# GitHub Issue Context Blocked\n\n"
        f"{message}\n\n"
        "Install and configure GitHub CLI on macOS with `brew install gh`, "
        "`gh auth login`, then verify with `gh auth status`. If you do not want "
        "to configure `gh` now, confirm that the issue body and key comments are "
        "pasted into the current session before planning continues.\n"
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", nargs="*", help="GitHub issue URL or text containing one")
    parser.add_argument(
        "--allow-multiple",
        action="store_true",
        help="Load every issue URL after the user confirms they share one context",
    )
    args = parser.parse_args(argv)

    text = " ".join(args.text)
    if not text and not sys.stdin.isatty():
        text = sys.stdin.read()

    issue_urls = extract_issue_urls(text)
    unsupported = extract_unsupported_github_urls(text, issue_urls)
    if unsupported and not issue_urls:
        print(render_blocked("Found GitHub URLs, but none are supported issue URLs."))
        for url in unsupported:
            print(f"- Unsupported: {url}")
        return 2
    if not issue_urls:
        print(render_blocked("No supported GitHub issue URL was found."))
        return 2
    if len(issue_urls) > 1 and not args.allow_multiple:
        print(
            render_blocked(
                "Multiple GitHub issue URLs were found. Ask the user to identify the primary issue, "
                "or rerun with `--allow-multiple` only after they confirm all issues share one requirement context."
            )
        )
        for url in issue_urls:
            print(f"- {url}")
        return 2
    if shutil.which("gh") is None:
        print(render_blocked("The `gh` command is not installed or not on PATH."))
        return 3

    rendered: list[str] = []
    for url in issue_urls:
        try:
            rendered.append(render_issue(run_gh(url)))
        except Exception as exc:  # noqa: BLE001 - surface CLI/auth failures as planning blockers
            print(render_blocked(f"`gh issue view` could not read {url}: {exc}"))
            return 4
    print("\n---\n\n".join(rendered), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
