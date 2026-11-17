"""Approved inception fixture for tests of unrelated execution behavior.

Readiness tests exercise real CLI transitions separately. This helper deliberately
writes fixture state directly; it is not a production approval shortcut.
"""
from uasef import cli


def approved_inception(project):
    state = cli.load(project)
    for item in state["tasks"]:
        item["status"] = "completed"
        if item["approval_required"]:
            item["approval_note"] = "Test fixture: owner reviewed and accepted inception artifacts"
        for rel in item["outputs"]:
            path = project / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Fixture evidence: scoped requirements, risks, acceptance and operational decisions reviewed. " * 3, encoding="utf-8")
    cli.write_json(cli.state_path(project), state)
    from uasef import memory
    memory.sync(project)
