# 🚓 Police Record Management System (PRMS)

A secure, scalable, and web-based **Police Record Management System** designed to digitize police records, streamline case workflows, and improve investigation efficiency using role-based access control and intelligent search.

---

## 📌 Project Overview

The **Police Record Management System (PRMS)** is a centralized digital platform that replaces traditional paper-based and fragmented police record systems.  
It enables law enforcement agencies to manage **FIRs, cases, suspects, evidence, and officer activities** in a secure, structured, and accountable manner.

The system closely follows **real-world police workflows**, including hierarchical approvals, station-level data isolation, and audit logging.

---

## 🎯 Objectives

- Digitize police records and case workflows  
- Enable fast and intelligent record searching  
- Enforce strict **Role-Based Access Control (RBAC)**  
- Maintain accountability through audit logs  
- Provide a scalable and modular architecture  

---

## 🚨 Problems Addressed

Traditional police systems suffer from:
- Fragmented paper records  
- Slow and exact-match-only searches  
- Weak access control  
- Lack of transparency and accountability  
- Difficulty tracking the complete case lifecycle  

PRMS resolves these issues through a modern, secure, web-based solution.

---

## ✨ Key Features

### 🔐 Role-Based Access Control (RBAC)
Different users have different permissions:
- **Admin** – Full system control  
- **Inspector / SHO** – Case approval and supervision  
- **Officer** – Case investigation and updates  
- **Constable** – FIR registration and limited access  

---

### 📂 Case Lifecycle Management
Complete workflow:FIR Created → Pending Approval → Approved → Under Investigation → Closed
---

### 🔍 Intelligent Fuzzy Search
- Handles spelling mistakes and name variations  
- Example: Searching `Sing` retrieves `Singh` or `Sinha`  
- Implemented using fuzzy string matching algorithms  

---

### 🧾 Audit Logging
- Logs every critical action (create, update, approve, delete)  
- Records user, action, timestamp, and IP address  
- Ensures transparency and accountability  

---

### 🏢 Station-Level Data Isolation
- Each police station can access only its own records  
- Prevents unauthorized cross-station access  

---

## 🛠️ Tech Stack

| Layer        | Technology |
|-------------|------------|
| Backend     | Python (Flask) |
| ORM         | SQLAlchemy |
| Frontend   | Jinja2 + Tailwind CSS |
| Database   | SQLite (Development) |
| Auth       | Flask-Login |
| Security   | CSRF Protection, PBKDF2 Password Hashing |
| Search     | RapidFuzz, Indic Transliteration |

---

## 🧱 System Architecture

- **Architecture Pattern:** MVC (Model-View-Controller)  
- **Modular Design:** Flask Blueprints  
- **Application Factory Pattern** for scalability  
- **ORM-based data modeling** for consistency and migration support  

---

## 🗄️ Database Design (Core Entities)

- **User** – Credentials, role, station mapping  
- **Case** – Central entity linking FIRs, suspects, evidence, and officers  
- **AuditLog** – Immutable record of system actions  
- **Station** – Enforces multi-tenancy and data isolation  

---

## 🔐 Security Implementation

- Role-based route protection using decorators  
- Station-scoped query filtering  
- CSRF protection for all forms  
- Secure password hashing using PBKDF2  
- Session management via Flask-Login  

---

## 🚀 Getting Started

### 📦 Prerequisites

- Python 3.9+  
- pip  
- virtualenv  

---

### 🧰 Installation

1. **Clone the repository**
```bash
git clone https://github.com/Gajanan9960/police-record-system.git
cd police-record-system
