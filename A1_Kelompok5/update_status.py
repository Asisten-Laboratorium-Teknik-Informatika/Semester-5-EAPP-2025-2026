from project_manager import get_projects, update_project_status

for p in get_projects():
    print(f"Updating project {p['id']} — {p['name']}")
    update_project_status(p["id"])

print("Done!")
