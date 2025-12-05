from project_manager import get_projects, update_project_status

projects = get_projects()

for p in projects:
    print(f"Updating '{p['name']}'")
    update_project_status(p["id"])

print("✓ DONE updating project statuses")
