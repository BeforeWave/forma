#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || true)
SELF_NAME=$(basename "${BASH_SOURCE[0]}")
ISSUE_WORKFLOW_INIT_DISABLED="1"

if [ -z "$REPO_ROOT" ]; then
  echo "Error: $SELF_NAME must be executed inside a git repository." >&2
  exit 1
fi

resolve_template_path() {
  local relative_path="$1"
  local package_reference_path="$SCRIPT_DIR/../references/$(basename "$relative_path")"
  local direct_path="$SCRIPT_DIR/$relative_path"

  if [ -f "$package_reference_path" ]; then
    printf '%s\n' "$package_reference_path"
    return
  fi

  if [ -f "$direct_path" ]; then
    printf '%s\n' "$direct_path"
    return
  fi

  printf '%s\n' "$direct_path"
}

PLAN_TEMPLATE=$(resolve_template_path "plan-first/dev/shared/plan-template.md")
TASKS_TEMPLATE=$(resolve_template_path "plan-first/dev/shared/tasks-template.md")

usage() {
  cat <<EOF
Usage:
  ./$SELF_NAME init <issue-id>
  ./$SELF_NAME status <issue-id>
  ./$SELF_NAME next <issue-id>
  ./$SELF_NAME notes-template <issue-id>
  ./$SELF_NAME review-ready <issue-id>
  ./$SELF_NAME complete <issue-id>
  ./$SELF_NAME <issue-id>   # alias for status
EOF
}

die() {
  echo "Error: $*" >&2
  exit 1
}

require_templates() {
  [ -f "$PLAN_TEMPLATE" ] || die "Missing plan template: $PLAN_TEMPLATE"
  [ -f "$TASKS_TEMPLATE" ] || die "Missing tasks template: $TASKS_TEMPLATE"
}

issue_paths() {
  ISSUE_ID="$1"
  PLAN_DIR="$REPO_ROOT/plans/issue-$ISSUE_ID"
  PLAN_FILE="$PLAN_DIR/plan.md"
  TASK_FILE="$PLAN_DIR/tasks.md"
  RUNS_DIR="$PLAN_DIR/runs"
  REVIEW_STATE_DIR="$REPO_ROOT/.forma-workflow/issue-$ISSUE_ID"
  REVIEW_STATE_FILE="$REVIEW_STATE_DIR/review-state.env"
  REVIEW_CHANGED_FILES_FILE="$REVIEW_STATE_DIR/changed-files.txt"
  REVIEW_CHANGED_SNAPSHOT_FILE="$REVIEW_STATE_DIR/changed-files.snapshot"
  REVIEW_VALIDATION_LOG="$REVIEW_STATE_DIR/validation.log"
}

ensure_issue_files_exist() {
  [ -f "$PLAN_FILE" ] || die "plan.md not found: $PLAN_FILE"
  [ -f "$TASK_FILE" ] || die "tasks.md not found: $TASK_FILE"
}

first_unchecked_task() {
  awk '
    /^(Task: )?- \[[ x]\] / {
      task_number++
      line = $0
      sub(/^Task: /, "", line)
      if (line ~ /^- \[ \] /) {
        print task_number "|" NR "|" substr(line, 7)
        exit
      }
    }
  ' "$TASK_FILE"
}

task_counts() {
  awk '
    /^(Task: )?- \[[ x]\] / {
      total++
      line = $0
      sub(/^Task: /, "", line)
      if (line ~ /^- \[x\] /) {
        done++
      }
    }
    END {
      printf "%d|%d\n", done, total
    }
  ' "$TASK_FILE"
}

task_format() {
  awk '
    /^(Task: )?- \[[ x]\] / {
      line = $0
      sub(/^Task: /, "", line)
      if (line ~ /^- \[[ x]\] \[[^]]+\] /) {
        print "structured"
      } else {
        print "legacy"
      }
      exit
    }
  ' "$TASK_FILE"
}

mark_task_complete() {
  local task_line="$1"
  local temp_file

  temp_file=$(mktemp)

  awk -v target_line="$task_line" '
    NR == target_line {
      if ($0 ~ /^Task: - \[ \] /) {
        sub(/^Task: - \[ \] /, "Task: - [x] ")
      } else if ($0 ~ /^- \[ \] /) {
        sub(/^- \[ \] /, "- [x] ")
      }
    }
    { print }
  ' "$TASK_FILE" >"$temp_file"

  mv "$temp_file" "$TASK_FILE"
}

plan_clean_status() {
  if ! git -C "$REPO_ROOT" ls-files --error-unmatch "$PLAN_FILE" >/dev/null 2>&1; then
    echo "untracked"
    return
  fi

  if ! git -C "$REPO_ROOT" diff --quiet -- "$PLAN_FILE"; then
    echo "modified"
    return
  fi

  if ! git -C "$REPO_ROOT" diff --cached --quiet -- "$PLAN_FILE"; then
    echo "staged"
    return
  fi

  echo "clean"
}

tasks_clean_status() {
  if ! git -C "$REPO_ROOT" ls-files --error-unmatch "$TASK_FILE" >/dev/null 2>&1; then
    echo "untracked"
    return
  fi

  if ! git -C "$REPO_ROOT" diff --quiet -- "$TASK_FILE"; then
    echo "modified"
    return
  fi

  if ! git -C "$REPO_ROOT" diff --cached --quiet -- "$TASK_FILE"; then
    echo "staged"
    return
  fi

  echo "clean"
}

collect_worktree_changed_files() {
  (
    cd "$REPO_ROOT"
    {
      git diff --name-only
      git diff --cached --name-only
      git ls-files --others --exclude-standard
    } | sed '/^$/d' | awk '$0 !~ /^\.forma-workflow\//' | sort -u
  )
}

collect_unstaged_files() {
  (
    cd "$REPO_ROOT"
    {
      git diff --name-only
      git ls-files --others --exclude-standard
    } | sed '/^$/d' | awk '$0 !~ /^\.forma-workflow\//' | sort -u
  )
}

parse_structured_tasks() {
  awk '
    function trim(value) {
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
      return value
    }
    function sanitize(value) {
      gsub(/\t/, "    ", value)
      return value
    }
    function fail(message) {
      print "Error: " message > "/dev/stderr"
      exit 1
    }
    function flush_task() {
      if (!in_task) {
        return
      }

      if (accept_count != 1) {
        fail("Structured task [" task_id "] must contain exactly one Accept: line.")
      }

      if (validate_mode == "") {
        fail("Structured task [" task_id "] must contain at least one Validate: line.")
      }

      if (validate_mode == "skip" && validate_count != 1) {
        fail("Structured task [" task_id "] must use exactly one review-only Validate: marker.")
      }

      print "TASK\t" task_number "\t" task_line "\t" task_status "\t" sanitize(task_id) "\t" sanitize(task_summary)
      print "ACCEPT\t" task_number "\t" sanitize(accept_text)
    }

    BEGIN {
      OFS = "\t"
    }

    /^[[:space:]]*$/ {
      next
    }

    {
      line = $0

      if (line ~ /^(Task: )?- \[[ x]\] \[[^]]+\] .+$/) {
        flush_task()

        normalized_line = line
        sub(/^Task: /, "", normalized_line)

        in_task = 1
        task_number++
        task_line = NR
        task_status = (substr(normalized_line, 4, 1) == "x" ? "checked" : "unchecked")

        task_payload = substr(normalized_line, 7)
        if (substr(task_payload, 1, 1) != "[") {
          fail("Structured task on line " NR " is missing the `[task-id]` prefix.")
        }

        closing_bracket = index(task_payload, "]")
        if (closing_bracket <= 2) {
          fail("Structured task on line " NR " is missing a valid task id.")
        }

        task_id = trim(substr(task_payload, 2, closing_bracket - 2))
        task_summary = trim(substr(task_payload, closing_bracket + 2))

        if (task_id == "") {
          fail("Structured task on line " NR " is missing a task id.")
        }
        if (task_summary == "") {
          fail("Structured task [" task_id "] must include a summary.")
        }
        if (task_id in seen_task_ids) {
          fail("Duplicate task id in " FILENAME ": " task_id)
        }

        seen_task_ids[task_id] = 1
        accept_count = 0
        accept_text = ""
        validate_mode = ""
        validate_count = 0
        depends_count = 0
        depends_none = 0
        next
      }

      if (!in_task) {
        fail("Unsupported content before the first task in " FILENAME ": " line)
      }

      if (index(line, "Accept:") == 1) {
        if (accept_count > 0) {
          fail("Structured task [" task_id "] must not repeat Accept:.")
        }

        accept_text = trim(substr(line, 8))
        if (accept_text == "") {
          fail("Structured task [" task_id "] has an empty Accept: line.")
        }

        accept_count++
        next
      }

      if (index(line, "Validate:") == 1) {
        validate_value = trim(substr(line, 10))

        if (validate_value == "") {
          fail("Structured task [" task_id "] has an empty Validate: line.")
        }

        if (validate_value ~ /^# no-programmatic-validation:/) {
          if (validate_mode == "command") {
            fail("Structured task [" task_id "] mixes executable Validate: commands with a review-only marker.")
          }
          if (validate_mode == "skip") {
            fail("Structured task [" task_id "] must use exactly one review-only Validate: marker.")
          }

          validate_reason = validate_value
          sub(/^# no-programmatic-validation:[[:space:]]*/, "", validate_reason)
          validate_reason = trim(validate_reason)
          if (validate_reason == "") {
            fail("Structured task [" task_id "] has an empty review-only Validate: reason.")
          }

          validate_mode = "skip"
          validate_count = 1
          print "VALIDATE_SKIP\t" task_number "\t" sanitize(validate_reason)
          next
        }

        if (validate_mode == "skip") {
          fail("Structured task [" task_id "] mixes executable Validate: commands with a review-only marker.")
        }

        validate_mode = "command"
        validate_count++
        print "VALIDATE_CMD\t" task_number "\t" sanitize(validate_value)
        next
      }

      if (index(line, "Use-Check:") == 1) {
        use_check_id = trim(substr(line, 11))
        if (use_check_id == "") {
          fail("Structured task [" task_id "] has an empty Use-Check: line.")
        }

        print "USE_CHECK\t" task_number "\t" sanitize(use_check_id)
        next
      }

      if (index(line, "Depends:") == 1) {
        depends_value = trim(substr(line, 9))
        if (depends_value == "") {
          fail("Structured task [" task_id "] has an empty Depends: line.")
        }
        if (depends_value ~ /^\[[^]]+\]$/) {
          fail("Structured task [" task_id "] must use bare task ids in Depends:, for example `Depends: " substr(depends_value, 2, length(depends_value) - 2) "`.")
        }

        if (depends_value == "none") {
          if (depends_none) {
            fail("Structured task [" task_id "] must not repeat Depends: none.")
          }
          if (depends_count > 0) {
            fail("Structured task [" task_id "] must not mix Depends: none with task ids.")
          }

          depends_none = 1
          next
        }

        if (depends_none) {
          fail("Structured task [" task_id "] must not mix Depends: none with task ids.")
        }
        if (depends_value == task_id) {
          fail("Structured task [" task_id "] must not depend on itself.")
        }

        depends_count++
        print "DEPENDS\t" task_number "\t" sanitize(depends_value)
        next
      }

      if (index(line, "Constraint:") == 1) {
        constraint_value = trim(substr(line, 12))
        if (constraint_value == "") {
          fail("Structured task [" task_id "] has an empty Constraint: line.")
        }

        print "CONSTRAINT\t" task_number "\t" sanitize(constraint_value)
        next
      }

      fail("Unsupported structured task line in " FILENAME ": " line)
    }

    END {
      flush_task()
    }
  ' "$TASK_FILE"
}

parse_structured_validation_checks() {
  awk '
    function trim(value) {
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
      return value
    }
    function sanitize(value) {
      gsub(/\t/, "    ", value)
      return value
    }
    function fail(message) {
      print "Error: " message > "/dev/stderr"
      exit 1
    }
    function flush_check() {
      if (!in_check) {
        return
      }

      if (check_command == "") {
        fail("Validation check [" check_id "] is missing Command:.")
      }

      print "CHECK\t" sanitize(check_id) "\t" sanitize(check_command)
      in_check = 0
      check_id = ""
      check_command = ""
    }

    BEGIN {
      OFS = "\t"
    }

    /^## Validation$/ {
      in_validation = 1
      next
    }

    /^## / {
      if (in_validation) {
        flush_check()
        exit
      }
    }

    !in_validation {
      next
    }

    /^[[:space:]]*$/ {
      next
    }

    {
      line = $0

      if (index(line, "Check:") == 1) {
        flush_check()

        check_id = trim(substr(line, 7))
        if (check_id == "") {
          fail("Validation check in " FILENAME " is missing an id.")
        }
        if (check_id in seen_checks) {
          fail("Duplicate validation check id in " FILENAME ": " check_id)
        }

        seen_checks[check_id] = 1
        in_check = 1
        next
      }

      if (index(line, "Command:") == 1) {
        if (!in_check) {
          fail("Command: must follow Check: in " FILENAME)
        }
        if (check_command != "") {
          fail("Validation check [" check_id "] must not repeat Command:.")
        }

        check_command = trim(substr(line, 9))
        if (check_command == "") {
          fail("Validation check [" check_id "] has an empty Command: line.")
        }

        next
      }

      if (index(line, "Note:") == 1) {
        if (!in_check) {
          fail("Note: must follow Check: in " FILENAME)
        }
        if (trim(substr(line, 6)) == "") {
          fail("Validation check [" check_id "] has an empty Note: line.")
        }

        next
      }

      fail("Unsupported validation line in " FILENAME ": " line)
    }

    END {
      if (in_validation) {
        flush_check()
      }
    }
  ' "$PLAN_FILE"
}

extract_fenced_validation_commands() {
  local heading="$1"

  awk -v heading="$heading" '
    $0 == heading {
      in_validation = 1
      next
    }
    /^## / {
      if (in_validation) {
        exit
      }
    }
    in_validation && /^```/ {
      if (!in_block) {
        in_block = 1
        next
      }
      exit
    }
    in_validation && in_block {
      print
    }
  ' "$PLAN_FILE"
}

classify_validation_failure() {
  local command="$1"
  local output_file="$2"

  if grep -Eq '(command not found|No such file or directory|unknown flag|flag provided but not defined)' "$output_file"; then
    printf 'tooling-env\n'
    return
  fi

  if grep -Eqi '(no such host|temporary failure in name resolution|connection refused|connection timed out|network is unreachable|TLS handshake timeout)' "$output_file"; then
    printf 'network\n'
    return
  fi

  if grep -Eqi '(Structured task|Unexpected change inside plans/|must use bare task ids|unknown shared check|No validation commands found|dependency is not complete|review-only Validate)' "$output_file"; then
    printf 'workflow-contract\n'
    return
  fi

  case "$command" in
    test\ !\ -d*|test\ !\ -f*)
      printf 'workflow-contract\n'
      return
      ;;
  esac

  printf 'code-test-regression\n'
}

report_validation_failure() {
  local scope="$1"
  local command="$2"
  local log_file="$3"
  local output_file="$4"
  local failure_class

  mkdir -p "$REVIEW_STATE_DIR"
  cp "$log_file" "$REVIEW_VALIDATION_LOG"
  cat "$output_file" >>"$REVIEW_VALIDATION_LOG"
  failure_class=$(classify_validation_failure "$command" "$output_file")
  {
    echo "Error: Validation step failed: $scope"
    echo "Command: $command"
    echo "Failure Class: $failure_class"
    echo "Validation Log: $REVIEW_VALIDATION_LOG"
  } >&2
}

run_logged_command() {
  local scope="$1"
  local command="$2"
  local log_file="$3"
  local output_file
  local -a clean_env

  output_file=$(mktemp)
  echo "Running validation [$scope]: $command"
  clean_env=(
    "PATH=${PATH:-/usr/bin:/bin}"
    "BASH_ENV="
    "ENV="
  )
  if [ -n "${HOME:-}" ]; then
    clean_env+=("HOME=$HOME")
  fi
  if [ -n "${TMPDIR:-}" ]; then
    clean_env+=("TMPDIR=$TMPDIR")
  fi

  if (
    cd "$REPO_ROOT"
    env -i "${clean_env[@]}" bash --noprofile --norc -c "$command"
  ) >"$output_file" 2>&1; then
    printf -- "- PASS [%s]: %s\n" "$scope" "$command" >>"$log_file"
  else
    printf -- "- FAIL [%s]: %s\n" "$scope" "$command" >>"$log_file"
    report_validation_failure "$scope" "$command" "$log_file" "$output_file"
    cat "$output_file" >&2
    rm -f "$output_file"
    return 1
  fi

  rm -f "$output_file"
}

validate_structured_task_dependencies() {
  local parsed_tasks_file="$1"
  local task_number="$2"

  awk -F'\t' -v task_number="$task_number" '
    $1 == "TASK" {
      task_status[$5] = $4
    }

    $1 == "DEPENDS" && $2 == task_number {
      dependencies[++dependency_count] = $3
    }

    END {
      for (dep_index = 1; dep_index <= dependency_count; dep_index++) {
        dependency_id = dependencies[dep_index]

        if (!(dependency_id in task_status)) {
          print "Error: Structured task references unknown dependency: " dependency_id > "/dev/stderr"
          exit 1
        }
        if (task_status[dependency_id] != "checked") {
          print "Error: Structured task dependency is not complete: " dependency_id > "/dev/stderr"
          exit 1
        }
      }
    }
  ' "$parsed_tasks_file"
}

structured_task_is_last_unchecked() {
  local parsed_tasks_file="$1"

  awk -F'\t' '
    $1 == "TASK" && $4 == "unchecked" {
      remaining++
    }
    END {
      exit !(remaining == 1)
    }
  ' "$parsed_tasks_file"
}

ensure_no_staged_changes() {
  git -C "$REPO_ROOT" diff --cached --quiet || die "Staged changes detected. Clear the index before running workflow commands."
}

ensure_planning_files_clean() {
  [ "$(plan_clean_status)" = "clean" ] || die "plan.md must be committed and unchanged before execution."
  [ "$(tasks_clean_status)" = "clean" ] || die "tasks.md must be committed and unchanged before execution."
}

ensure_task_exists() {
  local counts
  local completed
  local total

  counts=$(task_counts)
  IFS='|' read -r completed total <<EOF
$counts
EOF
  [ "$total" -gt 0 ] || die "No tasks have been defined in $TASK_FILE yet."
}

current_task_info() {
  local next_task

  next_task=$(first_unchecked_task || true)
  [ -n "$next_task" ] || die "All tasks are already completed."

  IFS='|' read -r CURRENT_TASK_NUMBER CURRENT_TASK_LINE CURRENT_TASK_TEXT <<EOF
$next_task
EOF
}

is_allowed_execution_plan_file() {
  local changed_file="$1"

  [ "$changed_file" = "plans/issue-$ISSUE_ID/implement-notes.md" ]
}

current_task_id_or_number() {
  case "$CURRENT_TASK_TEXT" in
    \[*\]*)
      local task_id="${CURRENT_TASK_TEXT#\[}"
      printf '%s\n' "${task_id%%\]*}"
      ;;
    *)
      printf 'task-%s\n' "$CURRENT_TASK_NUMBER"
      ;;
  esac
}

ensure_notes_format_if_changed() {
  local changed_files_file="$1"
  local notes_rel_path="plans/issue-$ISSUE_ID/implement-notes.md"
  local notes_file="$REPO_ROOT/$notes_rel_path"

  grep -Fxq "$notes_rel_path" "$changed_files_file" || return 0

  [ -f "$notes_file" ] || die "implement-notes.md changed for current issue but file is missing: $notes_rel_path"
  grep -qx '# Implement Notes' "$notes_file" || die "implement-notes.md must contain a '# Implement Notes' title."
  grep -q "^## Task $CURRENT_TASK_NUMBER: " "$notes_file" || die "implement-notes.md must contain a section for the current task: ## Task $CURRENT_TASK_NUMBER: $(current_task_id_or_number)"
  grep -qx 'Outcome:' "$notes_file" || die "implement-notes.md current task section must include an Outcome: field."
}

write_changed_files_file() {
  local destination="$1"
  local changed_files

  changed_files=$(collect_worktree_changed_files)
  [ -n "$changed_files" ] || die "No working tree changes found for the current task."

  while IFS= read -r changed_file; do
    [ -n "$changed_file" ] || continue
    case "$changed_file" in
      plans/*)
        if ! is_allowed_execution_plan_file "$changed_file"; then
          die "Unexpected change inside plans/: $changed_file"
        fi
        ;;
    esac
  done <<EOF
$changed_files
EOF

  printf '%s\n' "$changed_files" >"$destination"
  ensure_notes_format_if_changed "$destination"
}

write_index_changed_files_file() {
  local destination="$1"
  local changed_files

  changed_files=$(
    cd "$REPO_ROOT"
    git diff --cached --name-only --diff-filter=ACDMRTUXB | sed '/^$/d' | awk '$0 !~ /^\.forma-workflow\//' | sort -u
  )
  [ -n "$changed_files" ] || die "No staged review snapshot found for the current task."

  while IFS= read -r changed_file; do
    [ -n "$changed_file" ] || continue
    case "$changed_file" in
      plans/*)
        if ! is_allowed_execution_plan_file "$changed_file"; then
          die "Unexpected staged change inside plans/: $changed_file"
        fi
        ;;
    esac
  done <<EOF
$changed_files
EOF

  printf '%s\n' "$changed_files" >"$destination"
}

stage_changed_files_from_list() {
  local changed_files_file="$1"

  while IFS= read -r changed_file; do
    [ -n "$changed_file" ] || continue

    if [ -e "$REPO_ROOT/$changed_file" ] || git -C "$REPO_ROOT" ls-files --error-unmatch -- "$changed_file" >/dev/null 2>&1; then
      git -C "$REPO_ROOT" add -- "$changed_file"
    fi
  done <"$changed_files_file"
}

write_index_snapshot() {
  local changed_files_file="$1"
  local destination="$2"
  local index_blob

  : >"$destination"
  while IFS= read -r changed_file; do
    [ -n "$changed_file" ] || continue

    index_blob=$(git -C "$REPO_ROOT" ls-files --stage -- "$changed_file" | awk 'NR == 1 { print $2 }')
    if [ -n "$index_blob" ]; then
      printf '%s\t%s\n' "$changed_file" "$index_blob" >>"$destination"
    else
      printf '%s\t%s\n' "$changed_file" "DELETED" >>"$destination"
    fi
  done <"$changed_files_file"
}

compute_snapshot_fingerprint() {
  local snapshot_file="$1"

  git -C "$REPO_ROOT" hash-object --stdin <"$snapshot_file"
}

emit_changed_file_list() {
  local heading="$1"
  local changed_files_file="$2"
  local changed_file
  local file_category

  [ -s "$changed_files_file" ] || return 0

  echo "$heading" >&2
  while IFS= read -r changed_file; do
    [ -n "$changed_file" ] || continue
    file_category=$(categorize_changed_file "$changed_file")
    if [ -e "$REPO_ROOT/$changed_file" ]; then
      printf -- '- modified [%s]: %s\n' "$file_category" "$changed_file" >&2
    elif git -C "$REPO_ROOT" ls-files --error-unmatch -- "$changed_file" >/dev/null 2>&1; then
      printf -- '- removed [%s]: %s\n' "$file_category" "$changed_file" >&2
    else
      printf -- '- added [%s]: %s\n' "$file_category" "$changed_file" >&2
    fi
  done <"$changed_files_file"
}

categorize_changed_file() {
  local changed_file="$1"

  case "$changed_file" in
    docs/*|*.md)
      printf 'docs\n'
      ;;
    scripts/*|plan-first/*|direct/*|packaging/*|forma-workflow.sh)
      printf 'tooling-workflow\n'
      ;;
    *)
      printf 'task-files\n'
      ;;
  esac
}

write_stale_review_delta() {
  local current_snapshot_file="$1"
  local reviewed_snapshot_file="$2"
  local delta_file="$3"

  python3 - "$current_snapshot_file" "$reviewed_snapshot_file" "$delta_file" <<'PY'
from __future__ import annotations

import sys
from pathlib import Path


def load_snapshot(path: Path) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    if not path.exists():
        return snapshot
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rel_path, fingerprint = line.split("\t", 1)
        snapshot[rel_path] = fingerprint
    return snapshot


current = load_snapshot(Path(sys.argv[1]))
reviewed = load_snapshot(Path(sys.argv[2]))
destination = Path(sys.argv[3])

rows: list[str] = []
for rel_path in sorted(set(current) | set(reviewed)):
    current_value = current.get(rel_path)
    reviewed_value = reviewed.get(rel_path)
    if current_value == reviewed_value:
      continue
    if reviewed_value is None:
      status = "added"
    elif current_value is None:
      status = "removed"
    else:
      status = "modified"
    rows.append(f"{status}\t{rel_path}")

destination.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")
PY
}

emit_stale_review_cache_details() {
  local current_snapshot_file="$1"
  local reviewed_snapshot_file="$2"
  local delta_file
  local delta_found="0"
  local change_status
  local changed_file
  local file_category

  delta_file=$(mktemp)
  write_stale_review_delta "$current_snapshot_file" "$reviewed_snapshot_file" "$delta_file"

  while IFS=$'\t' read -r change_status changed_file; do
    [ -n "${change_status:-}" ] || continue
    if [ "$delta_found" = "0" ]; then
      echo "Post-review file changes:" >&2
      delta_found="1"
    fi
    file_category=$(categorize_changed_file "$changed_file")
    printf -- '- %s [%s]: %s\n' "$change_status" "$file_category" "$changed_file" >&2
  done <"$delta_file"

  rm -f "$delta_file"
}

append_structured_task_validation_records() {
  local parsed_tasks_file="$1"
  local task_number="$2"
  local records_file="$3"
  local record_type
  local record_task
  local record_value

  while IFS=$'\t' read -r record_type record_task record_value; do
    case "$record_type" in
      VALIDATE_CMD)
        printf 'CMD\t%s\t%s\n' "task" "$record_value" >>"$records_file"
        ;;
      VALIDATE_SKIP)
        printf 'NOTE\t%s\t%s\n' "task" "$record_value" >>"$records_file"
        ;;
    esac
  done < <(
    awk -F'\t' -v task_number="$task_number" '
      $2 == task_number && ($1 == "VALIDATE_CMD" || $1 == "VALIDATE_SKIP") {
        print $1 "\t" $2 "\t" $3
      }
    ' "$parsed_tasks_file"
  )
}

append_structured_shared_check_records() {
  local parsed_tasks_file="$1"
  local shared_checks_file="$2"
  local task_number="$3"
  local records_file="$4"
  local check_id
  local check_command

  while IFS= read -r check_id; do
    [ -n "$check_id" ] || continue

    check_command=$(
      awk -F'\t' -v check_id="$check_id" '
        $1 == "CHECK" && $2 == check_id {
          print $3
          found = 1
          exit
        }
        END {
          if (!found) {
            exit 1
          }
        }
      ' "$shared_checks_file"
    ) || die "Structured task references unknown shared check: $check_id"

    printf 'CMD\t%s\t%s\n' "shared-check:$check_id" "$check_command" >>"$records_file"
  done < <(
    awk -F'\t' -v task_number="$task_number" '
      $1 == "USE_CHECK" && $2 == task_number {
        print $3
      }
    ' "$parsed_tasks_file"
  )
}

append_fenced_validation_records() {
  local heading="$1"
  local scope="$2"
  local records_file="$3"
  local require_commands="$4"
  local found=0
  local no_programmatic_validation=""
  local command

  while IFS= read -r command; do
    case "$command" in
      \#\ no-programmatic-validation:*)
        no_programmatic_validation="${command#\# no-programmatic-validation: }"
        continue
        ;;
    esac

    case "$command" in
      "" | \#*)
        continue
        ;;
    esac

    found=1
    printf 'CMD\t%s\t%s\n' "$scope" "$command" >>"$records_file"
  done < <(extract_fenced_validation_commands "$heading")

  if [ "$found" -eq 0 ] && [ -n "$no_programmatic_validation" ]; then
    printf 'NOTE\t%s\t%s\n' "$scope" "$no_programmatic_validation" >>"$records_file"
    return 0
  fi

  if [ "$found" -eq 0 ] && [ "$require_commands" = "required" ]; then
    die "No validation commands found in section $heading of $PLAN_FILE"
  fi
}

deduplicate_validation_records() {
  local records_file="$1"
  local deduped_file="$2"

  awk -F'\t' '
    function normalize(value, normalized) {
      normalized = value
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", normalized)
      gsub(/[[:space:]]+/, " ", normalized)
      return normalized
    }
    function scope_present(existing, candidate) {
      split(existing, parts, /, /)
      for (idx in parts) {
        if (parts[idx] == candidate) {
          return 1
        }
      }
      return 0
    }

    {
      if ($1 == "NOTE") {
        index_count++
        record_type[index_count] = "NOTE"
        record_scope[index_count] = $2
        record_value[index_count] = $3
        next
      }

      if ($1 != "CMD") {
        next
      }

      key = normalize($3)
      if (!(key in command_index)) {
        index_count++
        command_index[key] = index_count
        record_type[index_count] = "CMD"
        record_scope[index_count] = $2
        record_value[index_count] = $3
        next
      }

      current_index = command_index[key]
      if (!scope_present(record_scope[current_index], $2)) {
        record_scope[current_index] = record_scope[current_index] ", " $2
      }
    }

    END {
      for (idx = 1; idx <= index_count; idx++) {
        print record_type[idx] "\t" record_scope[idx] "\t" record_value[idx]
      }
    }
  ' "$records_file" >"$deduped_file"
}

execute_validation_records() {
  local records_file="$1"
  local log_file="$2"
  local record_type
  local record_scope
  local record_value

  while IFS=$'\t' read -r record_type record_scope record_value; do
    case "$record_type" in
      CMD)
        run_logged_command "$record_scope" "$record_value" "$log_file" || return 1
        ;;
      NOTE)
        printf -- "- NOTE [%s]: no programmatic validation: %s\n" "$record_scope" "$record_value" >>"$log_file"
        ;;
    esac
  done <"$records_file"
}

write_review_state() {
  local current_task_format="$1"
  local current_task_number="$2"
  local current_task_line="$3"
  local current_task_text="$4"
  local is_last_task="$5"
  local fingerprint="$6"

  mkdir -p "$REVIEW_STATE_DIR"

  {
    printf 'REVIEW_TASK_FORMAT=%q\n' "$current_task_format"
    printf 'REVIEW_TASK_NUMBER=%q\n' "$current_task_number"
    printf 'REVIEW_TASK_LINE=%q\n' "$current_task_line"
    printf 'REVIEW_TASK_TEXT=%q\n' "$current_task_text"
    printf 'REVIEW_IS_LAST_TASK=%q\n' "$is_last_task"
    printf 'REVIEW_FINGERPRINT=%q\n' "$fingerprint"
    printf 'REVIEW_READY_AT=%q\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  } >"$REVIEW_STATE_FILE"
}

load_review_state() {
  [ -f "$REVIEW_STATE_FILE" ] || die "No review cache found for issue-$ISSUE_ID. Run review-ready first."

  REVIEW_TASK_FORMAT=""
  REVIEW_TASK_NUMBER=""
  REVIEW_TASK_LINE=""
  REVIEW_TASK_TEXT=""
  REVIEW_IS_LAST_TASK=""
  REVIEW_FINGERPRINT=""
  REVIEW_READY_AT=""
  # shellcheck disable=SC1090
  source "$REVIEW_STATE_FILE"

  [ -f "$REVIEW_CHANGED_FILES_FILE" ] || die "Review cache is incomplete for issue-$ISSUE_ID: missing changed files."
  [ -f "$REVIEW_CHANGED_SNAPSHOT_FILE" ] || die "Review cache is incomplete for issue-$ISSUE_ID: missing changed file snapshot."
  [ -f "$REVIEW_VALIDATION_LOG" ] || die "Review cache is incomplete for issue-$ISSUE_ID: missing validation log."
}

ensure_review_state_matches_current_task() {
  [ "$REVIEW_TASK_NUMBER" = "$CURRENT_TASK_NUMBER" ] || die "Review cache targets a different task. Re-run review-ready for the current task."
  [ "$REVIEW_TASK_TEXT" = "$CURRENT_TASK_TEXT" ] || die "Review cache targets a different task. Re-run review-ready for the current task."
}

clear_review_staging_for_current_task() {
  local changed_file

  [ -f "$REVIEW_STATE_FILE" ] || return 0
  [ -f "$REVIEW_CHANGED_FILES_FILE" ] || return 0

  REVIEW_TASK_NUMBER=""
  REVIEW_TASK_TEXT=""
  # shellcheck disable=SC1090
  source "$REVIEW_STATE_FILE"

  [ "${REVIEW_TASK_NUMBER:-}" = "$CURRENT_TASK_NUMBER" ] || return 0
  [ "${REVIEW_TASK_TEXT:-}" = "$CURRENT_TASK_TEXT" ] || return 0

  while IFS= read -r changed_file; do
    [ -n "$changed_file" ] || continue
    git -C "$REPO_ROOT" reset -q HEAD -- "$changed_file" >/dev/null 2>&1 || git -C "$REPO_ROOT" rm --cached -q --ignore-unmatch -- "$changed_file" >/dev/null 2>&1 || true
  done <"$REVIEW_CHANGED_FILES_FILE"
}

cmd_init() {
  if [ "$ISSUE_WORKFLOW_INIT_DISABLED" = "1" ]; then
    die "showhand is execution-only for an already-finalized plan; use finalize-plan to initialize or edit plan.md and tasks.md."
  fi

  require_templates
  issue_paths "$1"

  [ ! -d "$PLAN_DIR" ] || die "Issue directory already exists: $PLAN_DIR"

  mkdir -p "$RUNS_DIR"
  cp "$PLAN_TEMPLATE" "$PLAN_FILE"
  cp "$TASKS_TEMPLATE" "$TASK_FILE"

  cat <<EOF
Initialized plan workspace:
- $PLAN_FILE
- $TASK_FILE

Next:
1. Use the finalize-plan skill to fill in and commit plan.md and tasks.md.
2. Use the execution skill to implement the current task and present it for review.
3. After user approval, use the same execution skill again to run scripts/forma-workflow.sh complete $1
EOF
}

cmd_status() {
  issue_paths "$1"

  echo "Issue: issue-$1"
  echo "Directory: $PLAN_DIR"

  if [ ! -f "$PLAN_FILE" ]; then
    echo "Plan: missing"
  else
    echo "Plan: present ($(plan_clean_status))"
  fi

  if [ ! -f "$TASK_FILE" ]; then
    echo "Tasks: missing"
  else
    echo "Tasks: present ($(tasks_clean_status))"
    IFS='|' read -r completed total <<EOF
$(task_counts)
EOF
    echo "Progress: $completed/$total completed"

    next_task=$(first_unchecked_task || true)
    if [ -n "$next_task" ]; then
      IFS='|' read -r task_number task_line task_text <<EOF
$next_task
EOF
      echo "Next task: [$task_number] $task_text"
    else
      echo "Next task: none"
    fi
  fi

  if [ -f "$REVIEW_STATE_FILE" ]; then
    load_review_state
    echo "Review: ready for task [$REVIEW_TASK_NUMBER]"
  else
    echo "Review: none"
  fi
}

cmd_next() {
  issue_paths "$1"
  ensure_issue_files_exist
  ensure_task_exists
  current_task_info
  echo "$CURRENT_TASK_TEXT"
}

cmd_notes_template() {
  local task_id

  issue_paths "$1"
  ensure_issue_files_exist
  ensure_task_exists
  current_task_info
  task_id=$(current_task_id_or_number)

  cat <<EOF
# Implement Notes

## Task $CURRENT_TASK_NUMBER: $task_id

Outcome:
- <task result, metric change, or artifact effect>

Decision Notes:
- None beyond the task plan

Plan Gaps Found:
- None

Classifications:
- None

Deviations From Plan:
- None

Follow-ups:
- None
EOF
}

cmd_review_ready() {
  local issue_id="$1"
  local current_task_format
  local parsed_tasks_file=""
  local shared_checks_file=""
  local validation_records
  local deduped_records
  local validation_log
  local changed_files_file
  local fingerprint
  local is_last_task="0"

  issue_paths "$issue_id"
  ensure_issue_files_exist
  ensure_planning_files_clean
  ensure_task_exists
  current_task_info
  clear_review_staging_for_current_task
  ensure_no_staged_changes

  current_task_format=$(task_format)
  validation_records=$(mktemp)
  deduped_records=$(mktemp)
  validation_log=$(mktemp)
  changed_files_file=$(mktemp)
  : >"$validation_records"
  : >"$validation_log"

  if [ "$current_task_format" = "structured" ]; then
    parsed_tasks_file=$(mktemp)
    shared_checks_file=$(mktemp)

    parse_structured_tasks >"$parsed_tasks_file"
    parse_structured_validation_checks >"$shared_checks_file"
    validate_structured_task_dependencies "$parsed_tasks_file" "$CURRENT_TASK_NUMBER"
    append_structured_task_validation_records "$parsed_tasks_file" "$CURRENT_TASK_NUMBER" "$validation_records"
    append_structured_shared_check_records "$parsed_tasks_file" "$shared_checks_file" "$CURRENT_TASK_NUMBER" "$validation_records"

    if structured_task_is_last_unchecked "$parsed_tasks_file"; then
      is_last_task="1"
      append_fenced_validation_records "## Final Validation" "final" "$validation_records" "optional"
    fi
  else
    append_fenced_validation_records "## Validation" "legacy" "$validation_records" "required"
  fi

  deduplicate_validation_records "$validation_records" "$deduped_records"
  execute_validation_records "$deduped_records" "$validation_log"

  mkdir -p "$REVIEW_STATE_DIR"
  write_changed_files_file "$changed_files_file"
  stage_changed_files_from_list "$changed_files_file"
  write_index_changed_files_file "$changed_files_file"

  cp "$changed_files_file" "$REVIEW_CHANGED_FILES_FILE"
  write_index_snapshot "$changed_files_file" "$REVIEW_CHANGED_SNAPSHOT_FILE"
  fingerprint=$(compute_snapshot_fingerprint "$REVIEW_CHANGED_SNAPSHOT_FILE")
  cp "$validation_log" "$REVIEW_VALIDATION_LOG"
  write_review_state "$current_task_format" "$CURRENT_TASK_NUMBER" "$CURRENT_TASK_LINE" "$CURRENT_TASK_TEXT" "$is_last_task" "$fingerprint"

  rm -f "$validation_records" "$deduped_records" "$validation_log" "$changed_files_file" "$parsed_tasks_file" "$shared_checks_file"

  cat <<EOF
Review-ready task [$CURRENT_TASK_NUMBER] for issue-$issue_id
Validation Log: $REVIEW_VALIDATION_LOG
EOF
}

cmd_complete() {
  local issue_id="$1"
  local plan_rel_path
  local changed_files_file
  local current_snapshot_file
  local unstaged_changes_file
  local changed_files_display
  local changed_file
  local current_fingerprint
  local evidence_file
  local commit_hash
  local commit_message
  local task_backup=""
  local evidence_backup=""
  local evidence_existed="0"
  local finalize_started="0"
  local finalize_succeeded="0"

  cleanup_complete_failure() {
    if [ "$finalize_started" != "1" ] || [ "$finalize_succeeded" = "1" ]; then
      return
    fi

    git -C "$REPO_ROOT" reset -q HEAD -- "$TASK_FILE" >/dev/null 2>&1 || true
    git -C "$REPO_ROOT" reset -q HEAD -- "$evidence_file" >/dev/null 2>&1 || git -C "$REPO_ROOT" rm --cached -q --ignore-unmatch -- "$evidence_file" >/dev/null 2>&1 || true

    if [ -n "$task_backup" ] && [ -f "$task_backup" ]; then
      cp "$task_backup" "$TASK_FILE"
    fi

    if [ "$evidence_existed" = "1" ]; then
      if [ -n "$evidence_backup" ] && [ -f "$evidence_backup" ]; then
        cp "$evidence_backup" "$evidence_file"
      fi
    else
      rm -f "$evidence_file"
    fi
  }

  issue_paths "$issue_id"
  ensure_issue_files_exist
  plan_rel_path="plans/issue-$issue_id/plan.md"
  ensure_planning_files_clean
  ensure_task_exists
  current_task_info
  load_review_state
  ensure_review_state_matches_current_task

  changed_files_file=$(mktemp)
  current_snapshot_file=$(mktemp)
  unstaged_changes_file=$(mktemp)
  collect_unstaged_files >"$unstaged_changes_file"
  if [ -s "$unstaged_changes_file" ]; then
    emit_changed_file_list "Unstaged changes detected after review:" "$unstaged_changes_file"
    rm -f "$changed_files_file" "$current_snapshot_file" "$unstaged_changes_file"
    die "Unstaged changes detected after review. Re-run review-ready before completion."
  fi

  write_index_changed_files_file "$changed_files_file"
  write_index_snapshot "$changed_files_file" "$current_snapshot_file"
  current_fingerprint=$(compute_snapshot_fingerprint "$current_snapshot_file")

  if [ "$current_fingerprint" != "$REVIEW_FINGERPRINT" ]; then
    emit_stale_review_cache_details "$current_snapshot_file" "$REVIEW_CHANGED_SNAPSHOT_FILE"
    rm -f "$changed_files_file" "$current_snapshot_file" "$unstaged_changes_file"
    die "Review cache is stale for the current task. Re-run review-ready before completion."
  fi

  mkdir -p "$RUNS_DIR"
  evidence_file="$RUNS_DIR/task-$(printf '%03d' "$CURRENT_TASK_NUMBER").md"
  changed_files_display=$(sed 's/^/- /' "$changed_files_file")
  task_backup=$(mktemp)
  cp "$TASK_FILE" "$task_backup"
  if [ -f "$evidence_file" ]; then
    evidence_backup=$(mktemp)
    cp "$evidence_file" "$evidence_backup"
    evidence_existed="1"
  fi
  finalize_started="1"
  trap cleanup_complete_failure ERR

  cat >"$evidence_file" <<EOF
# Task Evidence

- Task: $CURRENT_TASK_TEXT
- Completed At (UTC): $(date -u +"%Y-%m-%dT%H:%M:%SZ")
- Commit Hash: Recorded in the commit that introduces this evidence file.

## Changed Files
$changed_files_display

## Validation Results
$(cat "$REVIEW_VALIDATION_LOG")

## Risks / Unresolved Items
- None recorded.
EOF

  mark_task_complete "$CURRENT_TASK_LINE"

  git -C "$REPO_ROOT" add -- "$TASK_FILE" "$evidence_file"

  commit_message=$(cat <<EOF
feat(issue-$issue_id): $CURRENT_TASK_TEXT

Plan:
- $plan_rel_path

Task:
- $CURRENT_TASK_TEXT
EOF
)

  git -C "$REPO_ROOT" commit -m "$commit_message" >/dev/null
  commit_hash=$(git -C "$REPO_ROOT" rev-parse HEAD)
  rm -rf "$REVIEW_STATE_DIR"
  finalize_succeeded="1"
  trap - ERR

  rm -f "$changed_files_file" "$current_snapshot_file" "$unstaged_changes_file" "$task_backup" "$evidence_backup"

  cat <<EOF
Completed task [$CURRENT_TASK_NUMBER] for issue-$issue_id
Commit: $commit_hash
Evidence: $evidence_file
EOF
}

main() {
  if [ "$#" -eq 0 ]; then
    usage
    exit 1
  fi

  case "$1" in
    init|status|next|notes-template|review-ready|complete)
      [ "$#" -eq 2 ] || die "Command '$1' requires exactly one <issue-id> argument."
      case "$1" in
        review-ready)
          cmd_review_ready "$2"
          ;;
        *)
          cmd_${1//-/_} "$2"
          ;;
      esac
      ;;
    -h|--help|help)
      usage
      ;;
    *)
      [ "$#" -eq 1 ] || die "Unknown command: $1"
      cmd_status "$1"
      ;;
  esac
}

main "$@"
