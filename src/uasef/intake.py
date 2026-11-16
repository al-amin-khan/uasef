"""A dependency-free intake interview; no filesystem changes before confirmation."""
from pathlib import Path


QUESTIONS = (
    ("users", "Who will use it?", "Not decided"),
    ("scope", "What must the first version do?", "Not decided"),
    ("excluded", "What should wait until later?", "Not decided"),
    ("stack", "Preferred technologies (or help me choose)?", "Help me choose"),
    ("constraints", "Budget, deadline, hosting or other constraints?", "Not decided"),
    ("success", "How will you know the first version succeeds?", "Not decided"),
)


def ask(label, default="", choices=()):
    while True:
        value = input(f"  {label}" + (f" [{default}]" if default else "") + ": ").strip() or default
        if value and (not choices or value in choices):
            return value
        print("  Choose: " + ", ".join(choices) if choices else "  Please enter an answer.")


def collect(args):
    print("\nUASEF / Guided project setup\nAnswer in plain language. Enter keeps the default; Ctrl+C cancels.\nDo not enter passwords, tokens, or other secrets.\n")
    answers = {}
    try:
        while True:
            answers["path"] = ask("Project folder", answers.get("path", args.path))
            target = Path(answers["path"]).expanduser().resolve()
            if (target / ".uasef" / "state.json").exists():
                raise ValueError("Project already initialized; choose a new folder.")
            if target.exists() and (not target.is_dir() or (any(target.iterdir()) and not args.existing)):
                raise ValueError("Target is not an empty folder. Use --existing to add UASEF to an existing project.")
            answers["name"] = ask("Project name", answers.get("name", args.name or target.name))
            answers["idea"] = ask("What do you want to build, and what problem does it solve?", answers.get("idea", args.idea or ""))
            for key, label, default in QUESTIONS:
                answers[key] = ask(label, answers.get(key, default))
            answers["adapter"] = ask("Coding assistant: codex, claude, copilot, opencode, all", answers.get("adapter", args.adapter), ("codex", "claude", "copilot", "opencode", "all"))
            print("\nReview project setup")
            for key, value in answers.items():
                print(f"  {key.title()}: {value}")
            print("\nThis creates UASEF planning files and instructions. It does not build the app or approve architecture.")
            choice = ask("Create project, edit answers, or cancel?", "cancel", ("create", "edit", "cancel"))
            if choice == "cancel":
                print("Cancelled. No project files created.")
                return False
            if choice == "edit":
                continue
            args.path = str(target)
            args.name = answers["name"]
            args.adapter = answers["adapter"]
            args.idea = answers["idea"] + "\n\n## Guided intake (user declarations; pending validation)\n\n" + "\n\n".join(f"### {label}\n\n{answers[key]}" for key, label, _ in QUESTIONS)
            return True
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled. No project files created.")
        return False
