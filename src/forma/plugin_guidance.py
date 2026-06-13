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
            "Before install:",
            f"  forma verify {resolved_root}",
            "  If this output came from a reviewed profile, run drift before any postprocess:",
            f"    forma drift {resolved_root} --profile <profile.yaml>",
            "  If you intentionally postprocess the generated artifact, run postprocess after drift",
            "  and use `forma verify` as the final gate for the postprocessed artifact.",
            "",
            "Recommended Codex install path:",
            "  During bootstrap discovery or diagnostics, inspect configured marketplaces as needed.",
            "  Ask the user to confirm the plugin id, marketplace name, marketplace source,",
            "  install selector, and visibility check.",
            "  Ensure the confirmed marketplace catalog points to the generated plugin root.",
            f"    codex plugin add {plugin_name}@<confirmed-marketplace>",
            "  Or install it from the Codex plugin UI.",
            "  Start a new Codex thread so the plugin skills are discovered.",
            "",
            "Fallback:",
            "  If Codex CLI output or marketplace behavior differs, consult current Codex docs or CLI help:",
            "    https://developers.openai.com/codex/plugins/build#install-a-local-plugin-manually",
            "    https://developers.openai.com/codex/plugins/build#add-a-marketplace-from-the-cli",
            "    codex plugin marketplace --help",
            "",
            "Forma does not install Codex plugins; Codex owns marketplace registration, install, and enabled state.",
        ]
    )
