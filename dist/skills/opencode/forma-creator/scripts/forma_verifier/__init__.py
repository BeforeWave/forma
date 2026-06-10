"""Layer 2 verifier — organizationally inside Layer 1's meta skill source.

Stdlib-only. The same package is also pip-installable via the root pyproject.toml's
`tool.setuptools.packages.find` configuration so that the developer-facing
`forma verify` CLI and the test suite can import it without subprocess hacks.
"""

from forma_verifier.runner import verify, classify_bundle, discover_skills
from forma_verifier.report import Report, RuleResult

__all__ = ["verify", "classify_bundle", "discover_skills", "Report", "RuleResult"]
__version__ = "0.1.1"
