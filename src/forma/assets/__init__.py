"""Packaged Forma runtime assets.

Wheel builds copy canonical `source/methodology` and `source/skill-creator`
trees under this package so the installed CLI can run without a source checkout.
Editable source checkouts may leave this package empty and use the development
fallback in `forma.runtime_assets`.
"""
