import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "smart-campus-secret")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": "codesage123",
    "database": os.getenv("DB_NAME", "smart_campus")
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def query(sql, params=(), fetch=True):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        if fetch:
            rows = cur.fetchall()
            return rows
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close()
        conn.close()

def scalar(sql, params=()):
    rows = query(sql, params)
    return list(rows[0].values())[0] if rows else 0

@app.route("/")
def dashboard():
    stats = {
        "events": scalar("SELECT COUNT(*) FROM events"),
        "students": scalar("SELECT COUNT(*) FROM students"),
        "resources": scalar("SELECT COUNT(*) FROM resources"),
        "registrations": scalar("SELECT COUNT(*) FROM registrations"),
    }
    upcoming = query("""
        SELECT e.*, r.name AS resource_name,
               (SELECT COUNT(*) FROM registrations x WHERE x.event_id=e.id) AS registrations
        FROM events e
        LEFT JOIN resources r ON e.resource_id=r.id
        WHERE e.event_date >= CURDATE()
        ORDER BY e.event_date, e.start_time
        LIMIT 6
    """)
    event_types = query("""
        SELECT event_type, COUNT(*) AS total,
               COALESCE(SUM(attendance),0) AS attendance
        FROM events GROUP BY event_type ORDER BY attendance DESC
    """)
    resource_usage = query("""
        SELECT r.name, r.capacity, COUNT(e.id) AS bookings,
               COALESCE(SUM(e.attendance),0) AS attendance
        FROM resources r
        LEFT JOIN events e ON e.resource_id=r.id
        GROUP BY r.id ORDER BY bookings DESC
    """)
    return render_template("dashboard.html", stats=stats, upcoming=upcoming,
                           event_types=event_types, resource_usage=resource_usage)

@app.route("/events")
def events():
    rows = query("""
        SELECT e.*, r.name AS resource_name,
               (SELECT COUNT(*) FROM registrations x WHERE x.event_id=e.id) AS registrations
        FROM events e
        LEFT JOIN resources r ON e.resource_id=r.id
        ORDER BY e.event_date DESC, e.start_time DESC
    """)
    resources = query("SELECT * FROM resources ORDER BY name")
    return render_template("events.html", events=rows, resources=resources)

@app.route("/events/add", methods=["POST"])
def add_event():
    title = request.form["title"].strip()
    event_type = request.form["event_type"]
    date = request.form["event_date"]
    start = request.form["start_time"]
    end = request.form["end_time"]
    resource_id = request.form.get("resource_id") or None
    organizer = request.form["organizer"].strip()
    expected = int(request.form.get("expected_attendance", 0))
    query("""INSERT INTO events
        (title,event_type,event_date,start_time,end_time,resource_id,organizer,expected_attendance)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        (title,event_type,date,start,end,resource_id,organizer,expected), fetch=False)
    flash("Event added successfully.", "success")
    return redirect(url_for("events"))

@app.route("/events/<int:event_id>/register", methods=["POST"])
def register(event_id):
    student_id = int(request.form["student_id"])
    try:
        query("INSERT INTO registrations (event_id, student_id) VALUES (%s,%s)",
              (event_id, student_id), fetch=False)
        flash("Student registered successfully.", "success")
    except Error as e:
        if getattr(e, "errno", None) == 1062:
            flash("Student is already registered for this event.", "warning")
        else:
            flash("Registration failed.", "danger")
    return redirect(url_for("events"))

@app.route("/resources")
def resources():
    rows = query("""
        SELECT r.*,
               COUNT(e.id) AS bookings,
               COALESCE(SUM(e.attendance),0) AS total_attendance
        FROM resources r
        LEFT JOIN events e ON e.resource_id=r.id
        GROUP BY r.id ORDER BY r.name
    """)
    return render_template("resources.html", resources=rows)

@app.route("/resources/add", methods=["POST"])
def add_resource():
    query("""INSERT INTO resources (name,resource_type,capacity,location)
             VALUES (%s,%s,%s,%s)""",
          (request.form["name"].strip(), request.form["resource_type"],
           int(request.form["capacity"]), request.form["location"].strip()), fetch=False)
    flash("Resource added successfully.", "success")
    return redirect(url_for("resources"))

@app.route("/students")
def students():
    rows = query("""
        SELECT s.*, COUNT(r.id) AS event_count
        FROM students s
        LEFT JOIN registrations r ON s.id=r.student_id
        GROUP BY s.id ORDER BY s.name
    """)
    return render_template("students.html", students=rows)

@app.route("/analytics")
def analytics():
    attendance = query("""
    SELECT
        DATE_FORMAT(event_date, '%b') AS month,
        COUNT(*) AS events,
        COALESCE(SUM(attendance), 0) AS attendance,
        COALESCE(SUM(expected_attendance), 0) AS expected
    FROM events
    GROUP BY YEAR(event_date), MONTH(event_date), DATE_FORMAT(event_date, '%b')
    ORDER BY YEAR(event_date), MONTH(event_date)
""")
    top_events = query("""
        SELECT title,event_type,event_date,attendance,expected_attendance,
               ROUND(IF(expected_attendance=0,0,attendance/expected_attendance*100),1) AS fill_rate
        FROM events ORDER BY attendance DESC LIMIT 8
    """)
    types = query("""
        SELECT event_type, COUNT(*) AS events,
               COALESCE(AVG(attendance),0) AS avg_attendance,
               COALESCE(AVG(expected_attendance),0) AS avg_expected
        FROM events GROUP BY event_type ORDER BY avg_attendance DESC
    """)
    utilization = query("""
        SELECT r.name, r.capacity, COUNT(e.id) AS bookings,
               COALESCE(SUM(e.attendance),0) AS attendance,
               ROUND(IF(COUNT(e.id)=0,0,SUM(e.attendance)/(COUNT(e.id)*r.capacity)*100),1) AS utilization
        FROM resources r LEFT JOIN events e ON r.id=e.resource_id
        GROUP BY r.id ORDER BY utilization DESC
    """)
    return render_template("analytics.html", attendance=attendance,
                           top_events=top_events, types=types, utilization=utilization)

@app.route("/api/insights")
def insights():
    avg = scalar("SELECT ROUND(AVG(attendance),0) FROM events")
    best = query("SELECT title, attendance FROM events ORDER BY attendance DESC LIMIT 1")
    resource = query("""
        SELECT r.name, COUNT(e.id) AS bookings
        FROM resources r LEFT JOIN events e ON r.id=e.resource_id
        GROUP BY r.id ORDER BY bookings DESC LIMIT 1
    """)
    return jsonify({
        "average_attendance": avg,
        "most_popular_event": best[0] if best else None,
        "most_used_resource": resource[0] if resource else None
    })

if __name__ == "__main__":
    app.run(debug=True)
