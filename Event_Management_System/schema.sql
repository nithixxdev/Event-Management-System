CREATE DATABASE IF NOT EXISTS smart_campus;
USE smart_campus;

CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    department VARCHAR(100) NOT NULL,
    year_level INT NOT NULL
);

CREATE TABLE IF NOT EXISTS resources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    resource_type VARCHAR(60) NOT NULL,
    capacity INT NOT NULL,
    location VARCHAR(120) NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    event_type VARCHAR(60) NOT NULL,
    event_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    resource_id INT,
    organizer VARCHAR(100) NOT NULL,
    expected_attendance INT DEFAULT 0,
    attendance INT DEFAULT 0,
    feedback_score DECIMAL(3,2) DEFAULT 0,
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    student_id INT NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_registration(event_id, student_id),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

INSERT INTO students (name,email,department,year_level) VALUES
('Arun Kumar','arun@campus.edu','AI & Data Science',3),
('Priya S','priya@campus.edu','Computer Science',2),
('Rahul M','rahul@campus.edu','Information Technology',4),
('Divya R','divya@campus.edu','Electronics',3),
('Karthik V','karthik@campus.edu','AI & Data Science',4),
('Meena P','meena@campus.edu','Computer Science',2)
ON DUPLICATE KEY UPDATE name=VALUES(name);

INSERT INTO resources (name,resource_type,capacity,location) VALUES
('Main Auditorium','Auditorium',500,'Block A'),
('Seminar Hall 1','Seminar Hall',180,'Block B'),
('Innovation Lab','Lab',80,'Block C'),
('Conference Room','Meeting Room',40,'Admin Block'),
('Open Air Stage','Stage',350,'Central Ground');

INSERT INTO events
(title,event_type,event_date,start_time,end_time,resource_id,organizer,expected_attendance,attendance,feedback_score)
VALUES
('AI Innovation Summit','Technical','2026-08-28','09:30:00','13:00:00',1,'Innovation Club',420,390,4.70),
('Python Bootcamp','Workshop','2026-08-30','10:00:00','15:00:00',3,'Coding Club',70,64,4.60),
('Placement Aptitude Challenge','Competition','2026-09-03','14:00:00','16:00:00',2,'Placement Cell',160,145,4.30),
('Entrepreneurship Meetup','Seminar','2026-09-07','11:00:00','13:00:00',2,'E-Cell',130,108,4.20),
('Cultural Fest','Cultural','2026-09-12','16:00:00','21:00:00',5,'Student Council',330,310,4.80),
('Cloud Computing Workshop','Workshop','2026-09-18','10:00:00','13:00:00',3,'Tech Club',75,61,4.40),
('Data Science Hackathon','Competition','2026-09-25','09:00:00','18:00:00',1,'AI Club',460,0,0),
('Alumni Career Talk','Seminar','2026-10-02','15:00:00','17:00:00',2,'Alumni Cell',150,0,0);
