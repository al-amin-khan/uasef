"""Local inception gates; declarations are not authenticated or a sandbox."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

PLANNING_SKILLS = {"project-inception", "requirements-discovery", "solution-research",
    "build-vs-buy", "product-specification", "technology-selection", "ux-design",
    "architecture-design", "data-modeling", "api-contracts", "security-review",
    "feature-planning", "quality-verification", "decision-records"}


def scope(inception_step=None, spike_reason="", spike_scope="", spike_hours=24):
    if inception_step and (spike_reason or spike_scope):
        raise ValueError("Choose an inception step or a feasibility spike")
    if inception_step:
        return {"kind": "inception", "step": inception_step}
    if spike_reason or spike_scope:
        if not all(isinstance(x, str) and 15 <= len(x.strip()) <= 500
                   for x in (spike_reason, spike_scope)):
            raise ValueError("Spike reason and scope must each contain 15-500 characters")
        if type(spike_hours) is not int or not 1 <= spike_hours <= 168:
            raise ValueError("Spike duration must be 1-168 hours")
        return {"kind": "spike", "reason": spike_reason.strip(), "scope": spike_scope.strip(),
                "expires_at": (datetime.now(timezone.utc) + timedelta(hours=spike_hours)).isoformat()}
    return {"kind": "implementation"}


def project_for(conn):
    filename = next(row[2] for row in conn.execute("PRAGMA database_list") if row[1] == "main")
    return Path(filename).parent.parent


def blocked(project, task):
    from . import cli
    try:
        policy = json.loads(task.get("readiness_scope", '{"kind":"implementation"}'))
        kind = policy["kind"]
        if kind == "spike":
            if not all(isinstance(policy.get(k), str) and 15 <= len(policy[k].strip()) <= 500
                       for k in ("reason", "scope")):
                return "Invalid recorded spike reason or scope"
            if datetime.fromisoformat(policy["expires_at"]) <= datetime.now(timezone.utc):
                return "Feasibility spike has expired; create a newly scoped task"
            if task.get("attempts", 0) >= 1:
                return "Feasibility spike permits one attempt; create a newly scoped task"
            return ""
        state = cli.load(project)
        canonical = cli.read_json(cli.framework_root() / "workflows/inception.json")["tasks"]
        steps = {item["id"]: item for item in state["tasks"]}
        if len(steps) != len(state["tasks"]):
            return "Duplicate inception steps in project state"
        expected = {item["id"]: item for item in canonical}
        if kind == "inception":
            current = expected[policy["step"]]
            if task["role"] != current["role"] or task["skill"] not in PLANNING_SKILLS:
                return "Inception task requires the step's role and a planning skill"
            if steps[current["id"]]["status"] not in ("pending", "in_progress"):
                return "Inception step is already submitted or completed"
            needed = set(current["depends_on"])
            while True:
                expanded = needed | {dep for key in needed for dep in expected[key]["depends_on"]}
                if expanded == needed:
                    break
                needed = expanded
        elif kind == "implementation":
            needed = set(expected)
        else:
            return "Unknown task readiness scope"
        for key in sorted(needed):
            item = steps[key]
            if item["status"] != "completed":
                return f"Inception {key} is incomplete; finish inception before implementation"
            if expected[key]["approval_required"] and len(item.get("approval_note", "").strip()) < 10:
                return f"Inception {key} requires a recorded approval"
            errors = cli.check_outputs(project, expected[key]["outputs"])
            if errors:
                return f"Inception {key} artifacts are unavailable or unfinished: {errors[0]}"
        return ""
    except (ValueError, TypeError, KeyError, OSError, AttributeError) as exc:
        return f"Invalid inception/readiness state: {type(exc).__name__}"
