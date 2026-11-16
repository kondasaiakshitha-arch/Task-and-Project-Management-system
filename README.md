# Task and Project Management Web Application

A Django-based project management app for collaborative planning, project tracking, and team productivity.

## Live app URL
Open the app locally here:

http://127.0.0.1:63193/

## Features
- Secure registration, login, and logout
- Project creation with owner/manager/member roles
- Task creation, assignment, priority, status, and deadline tracking
- Dashboard with progress metrics and workload summaries
- Kanban drag-and-drop task board
- Search and filter support for tasks
- Comments, file attachments, and activity log tracking
- Dashboard charting and project completion insights

## Tech stack
- Python 3.10+
- Django 5.0.6
- SQLite for local development
- Bootstrap 5 and Chart.js for the UI

## Folder structure
- `accounts/` — registration, login, and profile views
- `projects/` — project model, membership logic, dashboard, and permissions
- `tasks/` — task, comments, attachments, board, and activity features
- `templates/` — all HTML pages for the app
- `static/` — CSS styling
- `taskmanager/` — Django project settings and URL routing
- `manage.py` — Django management entry point

## How to run the project in terminal
From the project folder, run the following commands:

```powershell
cd "C:\Users\saiak\Downloads\Task and Project Management"
.\.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver 127.0.0.1:63193
```

Then open this in the browser:

```text
http://127.0.0.1:63193/
```

## If you need to create an admin user
```powershell
cd "C:\Users\saiak\Downloads\Task and Project Management"
.\.venv\Scripts\Activate.ps1
python manage.py createsuperuser
```

## If the port is busy
Use a free port, for example:

```powershell
cd "C:\Users\saiak\Downloads\Task and Project Management"
.\.venv\Scripts\Activate.ps1
python manage.py runserver 127.0.0.1:8000
```

Then open:

```text
http://127.0.0.1:8000/
```

## Notes
- The app uses SQLite locally for simplicity.
- For production, you can later switch to PostgreSQL and deploy to Render or Railway.
- The project is already working and verified locally.

## ER diagram summary
- User has many owned projects
- Project has many members through the `Membership` model
- Project has many tasks
- Task has many comments, attachments, and activity logs
