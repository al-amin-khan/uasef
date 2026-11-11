"""Deterministic, explainable provider profile selection. No network calls.

Profiles describe user-installed tools; a profile is not proof that a provider,
model or sandbox is available. Never silently fallback after execution starts.
"""
from __future__ import annotations


def _candidates(config, task):
    routing = config.get("routing", {})
    if not isinstance(routing, dict):
        raise ValueError("routing must be an object")
    by_role = routing.get("by_role", {})
    defaults = routing.get("defaults", [])
    if not isinstance(by_role, dict) or not isinstance(defaults, list):
        raise ValueError("routing.by_role must be a map and defaults must be an array")
    candidates = by_role.get(task["role"], defaults)
    if not isinstance(candidates, list):
        raise ValueError("Role route must be an array")
    return candidates


def evaluate(config, task):
    profiles = config.get("profiles", {})
    if not isinstance(profiles, dict):
        raise ValueError("Runner profiles must be an object")
    found = []
    for name in _candidates(config, task):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Routing entries must be profile names")
        p = profiles.get(name)
        reason = None
        if not isinstance(p, dict) or p.get("type") not in ("subprocess", "opencode"):
            reason = "not a configured executable runner"
        elif p.get("enabled", True) is not True:
            reason = "profile disabled"
        elif p.get("roles") is not None and task["role"] not in p["roles"]:
            reason = "role not permitted"
        elif p.get("skills") is not None and task["skill"] not in p["skills"]:
            reason = "skill not permitted"
        found.append({"profile": name, "eligible": reason is None, "reason": reason or "matches role and skill"})
    return found


def select(config, task):
    choices = evaluate(config, task)
    for candidate in choices:
        if candidate["eligible"]:
            return candidate["profile"]
    raise ValueError("No eligible automatic runner profile. Configure routing and subprocess profiles; never silently execute manual mode.")
