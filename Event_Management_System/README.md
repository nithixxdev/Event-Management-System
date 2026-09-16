# Smart Campus Resource & Event Intelligence System

A Flask + MySQL campus intelligence dashboard for event management, resource utilization, student participation and analytics.

## Features
- Dashboard with campus KPIs
- Event creation and registration
- Student participation tracking
- Campus resource management
- Event attendance analytics
- Resource utilization analytics
- Event-type comparison
- Top event performance
- JSON insights API

## Requirements
- Python 3.10+
- MySQL 8+
- pip

## Run

### 1. Create the database
Open MySQL Workbench or MySQL terminal and run:

```sql
SOURCE schema.sql;
```

### 2. Install packages

```bash
pip install -r requirements.txt
```

### 3. Configure MySQL

Set environment variables or edit the defaults in `app.py`.

Windows PowerShell example:

```powershell
$env:DB_USER="root"
$env:DB_PASSWORD="your_password"
$env:DB_NAME="smart_campus"
```

### 4. Start

```bash
python app.py
```

Open http://127.0.0.1:5000

## Project structure

smart_campus/
├── app.py
├── schema.sql
├── requirements.txt
├── .env.example
├── README.md
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── events.html
│   ├── resources.html
│   ├── students.html
│   └── analytics.html
└── static/
    └── style.css

## Portfolio direction

The current version is an MVP. For a stronger final resume project, add:
- Attendance prediction model
- Venue recommendation
- Login/role management
- CSV upload
- Event feedback collection
- Power BI dashboard
- Automated monthly reports
