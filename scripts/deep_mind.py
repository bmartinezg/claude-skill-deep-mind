#!/usr/bin/env python3
"""
Deep Mind - Shared brain management for multi-project matrices.

Usage:
    deep_mind.py init <matrix>
    deep_mind.py register <matrix> <project-name> [--path <path>]
    deep_mind.py unregister <matrix> <project-name>
    deep_mind.py status [<matrix>]
    deep_mind.py list
    deep_mind.py projects <matrix>
    deep_mind.py add-vertical <matrix> <vertical-name>
    deep_mind.py remove-vertical <matrix> <vertical-name>
    deep_mind.py list-verticals <matrix>
    deep_mind.py read <matrix> [<vertical>]
    deep_mind.py log <matrix> <message>
    deep_mind.py detect
    deep_mind.py path <matrix>
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

BASE_DIR = Path.home() / ".claude" / "deep-mind"


def get_matrix_dir(name):
    return BASE_DIR / name


def load_manifest(matrix):
    manifest_path = get_matrix_dir(matrix) / "manifest.json"
    if not manifest_path.exists():
        return None
    return json.loads(manifest_path.read_text())


def save_manifest(matrix, manifest):
    manifest_path = get_matrix_dir(matrix) / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))


def init_matrix(name):
    mdir = get_matrix_dir(name)
    if mdir.exists():
        print(f"Matrix '{name}' already exists at {mdir}")
        return True

    mdir.mkdir(parents=True)

    manifest = {
        "name": name,
        "created": datetime.now().isoformat(),
        "projects": {},
        "verticals": [],
    }
    save_manifest(name, manifest)

    (mdir / "changelog.md").write_text(
        f"# Changelog\n\n## {datetime.now().strftime('%Y-%m-%d %H:%M')}\n- Matrix '{name}' created\n"
    )

    print(f"Matrix '{name}' initialized at {mdir}")
    return True


def register_project(matrix, project_name, project_path=None):
    mdir = get_matrix_dir(matrix)
    if not mdir.exists():
        print(f"Error: Matrix '{matrix}' does not exist. Run init first.")
        return False

    manifest = load_manifest(matrix)
    path = project_path or os.getcwd()

    manifest["projects"][project_name] = {
        "path": str(path),
        "registered": datetime.now().isoformat(),
    }
    save_manifest(matrix, manifest)

    project_config = {
        "matrix": matrix,
        "project": project_name,
        "registered": datetime.now().isoformat(),
    }
    config_path = Path(path) / ".deep-mind.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(project_config, indent=2))

    log_change(matrix, f"Project '{project_name}' registered ({path})")

    print(f"Project '{project_name}' registered under '{matrix}'")
    print(f"Config written to: {config_path}")
    return True


def unregister_project(matrix, project_name):
    mdir = get_matrix_dir(matrix)
    if not mdir.exists():
        print(f"Error: Matrix '{matrix}' does not exist.")
        return False

    manifest = load_manifest(matrix)

    if project_name not in manifest["projects"]:
        print(f"Error: Project '{project_name}' not found in '{matrix}'.")
        return False

    project_path = manifest["projects"][project_name].get("path")
    del manifest["projects"][project_name]
    save_manifest(matrix, manifest)

    if project_path:
        config_path = Path(project_path) / ".deep-mind.json"
        if config_path.exists():
            config_path.unlink()

    log_change(matrix, f"Project '{project_name}' unregistered")
    print(f"Project '{project_name}' removed from '{matrix}'")
    return True


def add_vertical(matrix, vertical_name):
    mdir = get_matrix_dir(matrix)
    if not mdir.exists():
        print(f"Error: Matrix '{matrix}' does not exist.")
        return False

    manifest = load_manifest(matrix)

    if vertical_name in manifest["verticals"]:
        print(f"Vertical '{vertical_name}' already exists in '{matrix}'.")
        return True

    manifest["verticals"].append(vertical_name)
    save_manifest(matrix, manifest)

    # Create empty vertical file if it doesn't exist
    vertical_file = mdir / f"{vertical_name}.md"
    if not vertical_file.exists():
        vertical_file.write_text(f"# {vertical_name.replace('-', ' ').title()}\n")

    log_change(matrix, f"Vertical '{vertical_name}' added")
    print(f"Vertical '{vertical_name}' added to '{matrix}'")
    print(f"File: {vertical_file}")
    return True


def remove_vertical(matrix, vertical_name):
    mdir = get_matrix_dir(matrix)
    if not mdir.exists():
        print(f"Error: Matrix '{matrix}' does not exist.")
        return False

    manifest = load_manifest(matrix)

    if vertical_name not in manifest["verticals"]:
        print(f"Error: Vertical '{vertical_name}' not found in '{matrix}'.")
        return False

    manifest["verticals"].remove(vertical_name)
    save_manifest(matrix, manifest)

    vertical_file = mdir / f"{vertical_name}.md"
    if vertical_file.exists():
        vertical_file.unlink()

    log_change(matrix, f"Vertical '{vertical_name}' removed")
    print(f"Vertical '{vertical_name}' removed from '{matrix}'")
    return True


def list_verticals(matrix):
    mdir = get_matrix_dir(matrix)
    if not mdir.exists():
        print(f"Error: Matrix '{matrix}' does not exist.")
        return

    manifest = load_manifest(matrix)
    verticals = manifest.get("verticals", [])

    if not verticals:
        print(f"No verticals in '{matrix}'.")
        return

    for v in verticals:
        vfile = mdir / f"{v}.md"
        if vfile.exists():
            content = vfile.read_text().strip()
            lines = [
                l
                for l in content.split("\n")
                if l.strip() and not l.strip().startswith("#")
            ]
            status = f"{len(lines)} lines" if lines else "empty"
        else:
            status = "no file"
        print(f"  {v}: {status}")


def list_matrices():
    if not BASE_DIR.exists():
        print("No matrices found.")
        return

    dirs = [
        d
        for d in BASE_DIR.iterdir()
        if d.is_dir() and (d / "manifest.json").exists()
    ]
    if not dirs:
        print("No matrices found.")
        return

    for d in sorted(dirs):
        manifest = json.loads((d / "manifest.json").read_text())
        pc = len(manifest.get("projects", {}))
        vc = len(manifest.get("verticals", []))
        print(f"  {d.name} ({pc} projects, {vc} verticals)")


def show_status(matrix=None):
    if not matrix:
        config = detect_project()
        if config:
            matrix = config["matrix"]
        else:
            list_matrices()
            return

    mdir = get_matrix_dir(matrix)
    if not mdir.exists():
        print(f"Error: Matrix '{matrix}' not found.")
        return

    manifest = load_manifest(matrix)

    print(f"Matrix: {manifest['name']}")
    print(f"Created: {manifest['created'][:10]}")

    print(f"\nProjects ({len(manifest['projects'])}):")
    for pname, pinfo in manifest["projects"].items():
        print(f"  - {pname}: {pinfo['path']}")

    verticals = manifest.get("verticals", [])
    print(f"\nVerticals ({len(verticals)}):")
    for v in verticals:
        vfile = mdir / f"{v}.md"
        if vfile.exists():
            content = vfile.read_text().strip()
            lines = [
                l
                for l in content.split("\n")
                if l.strip() and not l.strip().startswith("#")
            ]
            status = f"{len(lines)} lines" if lines else "empty"
        else:
            status = "no file"
        print(f"  - {v}: {status}")

    if not verticals:
        print("  (none)")


def list_projects(matrix):
    mdir = get_matrix_dir(matrix)
    if not mdir.exists():
        print(f"Error: Matrix '{matrix}' not found.")
        return

    manifest = load_manifest(matrix)

    if not manifest["projects"]:
        print(f"No projects in '{matrix}'.")
        return

    for pname, pinfo in manifest["projects"].items():
        print(f"  {pname}: {pinfo['path']}")


def read_brain(matrix, vertical=None):
    mdir = get_matrix_dir(matrix)
    if not mdir.exists():
        print(f"Error: Matrix '{matrix}' not found.")
        return

    manifest = load_manifest(matrix)
    verticals = manifest.get("verticals", [])

    if vertical:
        if vertical not in verticals:
            print(f"Error: Vertical '{vertical}' not registered in '{matrix}'.")
            print(f"Available: {', '.join(verticals)}")
            return
        vfile = mdir / f"{vertical}.md"
        if not vfile.exists():
            print(f"Error: File for vertical '{vertical}' not found.")
            return
        print(vfile.read_text())
    else:
        if not verticals:
            print(f"No verticals in '{matrix}'.")
            return
        for v in verticals:
            vfile = mdir / f"{v}.md"
            if vfile.exists():
                print(vfile.read_text())
                print()


def log_change(matrix, message):
    mdir = get_matrix_dir(matrix)
    changelog = mdir / "changelog.md"

    entry = f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M')}\n- {message}\n"

    if changelog.exists():
        content = changelog.read_text()
        lines = content.split("\n", 1)
        if len(lines) > 1:
            content = lines[0] + "\n" + entry + lines[1]
        else:
            content = lines[0] + "\n" + entry
        changelog.write_text(content)
    else:
        changelog.write_text(f"# Changelog\n{entry}")


def detect_project():
    config_path = Path(os.getcwd()) / ".deep-mind.json"
    if config_path.exists():
        return json.loads(config_path.read_text())
    return None


def get_brain_path(matrix):
    print(str(get_matrix_dir(matrix)))


def main():
    if len(sys.argv) < 2:
        print("Usage: deep_mind.py <command> [args]")
        print("\nCommands:")
        print("  init <matrix>                              Create new matrix")
        print("  register <matrix> <project> [--path <p>]   Register project")
        print("  unregister <matrix> <project>              Remove project")
        print("  status [<matrix>]                          Show status")
        print("  list                                       List all matrices")
        print("  projects <matrix>                          List projects")
        print("  add-vertical <matrix> <name>               Add vertical to matrix")
        print("  remove-vertical <matrix> <name>            Remove vertical")
        print("  list-verticals <matrix>                    List verticals")
        print("  read <matrix> [<vertical>]                 Read brain content")
        print("  log <matrix> <message>                     Add changelog entry")
        print("  detect                                     Detect project in cwd")
        print("  path <matrix>                              Print brain directory path")
        print(f"\nBrain storage: {BASE_DIR}")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "init":
        if len(sys.argv) < 3:
            print("Usage: deep_mind.py init <matrix-name>")
            sys.exit(1)
        init_matrix(sys.argv[2])

    elif cmd == "register":
        if len(sys.argv) < 4:
            print("Usage: deep_mind.py register <matrix> <project-name> [--path <path>]")
            sys.exit(1)
        path = None
        if "--path" in sys.argv:
            idx = sys.argv.index("--path")
            if idx + 1 < len(sys.argv):
                path = sys.argv[idx + 1]
        register_project(sys.argv[2], sys.argv[3], path)

    elif cmd == "unregister":
        if len(sys.argv) < 4:
            print("Usage: deep_mind.py unregister <matrix> <project-name>")
            sys.exit(1)
        unregister_project(sys.argv[2], sys.argv[3])

    elif cmd == "status":
        mat = sys.argv[2] if len(sys.argv) > 2 else None
        show_status(mat)

    elif cmd == "list":
        list_matrices()

    elif cmd == "projects":
        if len(sys.argv) < 3:
            print("Usage: deep_mind.py projects <matrix>")
            sys.exit(1)
        list_projects(sys.argv[2])

    elif cmd == "add-vertical":
        if len(sys.argv) < 4:
            print("Usage: deep_mind.py add-vertical <matrix> <vertical-name>")
            sys.exit(1)
        add_vertical(sys.argv[2], sys.argv[3])

    elif cmd == "remove-vertical":
        if len(sys.argv) < 4:
            print("Usage: deep_mind.py remove-vertical <matrix> <vertical-name>")
            sys.exit(1)
        remove_vertical(sys.argv[2], sys.argv[3])

    elif cmd == "list-verticals":
        if len(sys.argv) < 3:
            print("Usage: deep_mind.py list-verticals <matrix>")
            sys.exit(1)
        list_verticals(sys.argv[2])

    elif cmd == "read":
        if len(sys.argv) < 3:
            print("Usage: deep_mind.py read <matrix> [<vertical>]")
            sys.exit(1)
        v = sys.argv[3] if len(sys.argv) > 3 else None
        read_brain(sys.argv[2], v)

    elif cmd == "log":
        if len(sys.argv) < 4:
            print("Usage: deep_mind.py log <matrix> <message>")
            sys.exit(1)
        log_change(sys.argv[2], " ".join(sys.argv[3:]))
        print("Logged.")

    elif cmd == "detect":
        result = detect_project()
        if result:
            print(json.dumps(result, indent=2))
        else:
            print("No .deep-mind.json found in current directory.")

    elif cmd == "path":
        if len(sys.argv) < 3:
            print("Usage: deep_mind.py path <matrix>")
            sys.exit(1)
        get_brain_path(sys.argv[2])

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
