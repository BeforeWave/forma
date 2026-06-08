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
            "Install with Codex:",
            "  Follow the current Codex docs instead of Forma-specific marketplace instructions:",
            "    https://developers.openai.com/codex/plugins/build#install-a-local-plugin-manually",
            "    https://developers.openai.com/codex/plugins/build#add-a-marketplace-from-the-cli",
            "  Useful commands after the plugin is in a Codex marketplace:",
            "    codex plugin marketplace list",
            f"    codex plugin add {plugin_name}@<marketplace-name>",
            "  Or install it from the Codex plugin UI.",
            "  Start a new Codex thread so the plugin skills are discovered.",
            "",
            "Forma does not install Codex plugins; Codex owns marketplace registration, install, and enabled state.",
        ]
    )
