"""Guidance for handing generated Codex plugin artifacts to Codex."""

from __future__ import annotations

import json
from pathlib import Path


def codex_plugin_name(plugin_root: Path) -> str:
    """Return the Codex plugin name from plugin.json when available."""
    plugin_json = plugin_root / ".codex-plugin" / "plugin.json"
    try:
        data = json.loads(plugin_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return plugin_root.name or "<plugin>"
    if not isinstance(data, dict):
        return plugin_root.name or "<plugin>"
    for key in ("name", "id"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return plugin_root.name or "<plugin>"


def codex_plugin_install_hint(plugin_root: Path) -> str:
    """Format actionable Codex marketplace install guidance for a local plugin."""
    resolved_root = plugin_root.resolve()
    plugin_name = codex_plugin_name(resolved_root)
    return "\n".join(
        [
            "Codex plugin generated, not installed.",
            "",
            "Plugin:",
            f"  name: {plugin_name}",
            f"  root: {resolved_root}",
            "",
            "Names:",
            "  marketplace root path: a directory containing .agents/plugins/marketplace.json",
            "  marketplace name: the MARKETPLACE value shown by `codex plugin marketplace list`",
            "  mapping: <marketplace-root-path>/.agents/plugins/marketplace.json has top-level `name: <marketplace-name>`",
            "  plugin entry: plugins[].name is the plugin name; plugins[].source.path points from marketplace root path to the plugin root",
            "",
            "Install with Codex:",
            "  1. Discover configured marketplaces:",
            "     codex plugin marketplace list",
            "  2. If the list shows a marketplace you want, use its MARKETPLACE as <marketplace-name> and ROOT as <marketplace-root-path>.",
            "     Add/copy this plugin under that ROOT and point plugins[].source.path at it.",
            "  3. If no suitable marketplace exists, choose a marketplace root path, create <marketplace-root-path>/.agents/plugins/marketplace.json, set its top-level `name`, and add this plugin under plugins[].",
            "     common source.path: ./plugins/<plugin-name> relative to marketplace root path",
            "  4. If that marketplace root path is not shown by `codex plugin marketplace list`, register it:",
            "     codex plugin marketplace add <marketplace-root-path>",
            "  5. Install from the marketplace:",
            f"     codex plugin add {plugin_name}@<marketplace-name>",
            f"     example only if `codex plugin marketplace list` shows `personal`: codex plugin add {plugin_name}@personal",
            "  6. Start a new Codex thread so the plugin skills are discovered.",
            "",
            "Forma does not install Codex plugins; Codex owns marketplace registration, install, and enabled state.",
        ]
    )
