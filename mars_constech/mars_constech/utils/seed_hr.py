import frappe, json
from datetime import date, timedelta

# Seed data mirroring the PWA's mockEmployees/mockLeave/mockHRAttendance
EMPLOYEES = [
    {"id": 1, "name": "Rofiqul Islam", "designation": "Site Engineer", "dept": "Construction", "phone": "01711112222", "email": "rofiqul@mars.com", "join": "2022-03-01", "salary": 65000, "status": "active", "ctype": "Permanent", "cstart": "2022-03-01", "cend": "2027-02-28", "notice": 30, "ins": "Green Delta Insurance", "policy": "GD-EMP-1001", "cov": 1000000, "iexp": "2027-03-01"},
    {"id": 2, "name": "Shamim Reza", "designation": "Sales Manager", "dept": "Sales", "phone": "01733335555", "email": "shamim@mars.com", "join": "2021-06-15", "salary": 85000, "status": "active", "ctype": "Permanent", "cstart": "2021-06-15", "cend": "2026-12-31", "notice": 60, "ins": "Green Delta Insurance", "policy": "GD-EMP-1002", "cov": 1500000, "iexp": "2026-07-10"},
    {"id": 3, "name": "Nazma Akhter", "designation": "Accountant", "dept": "Finance", "phone": "01755557777", "email": "nazma@mars.com", "join": "2023-01-10", "salary": 55000, "status": "active", "ctype": "Permanent", "cstart": "2023-01-10", "cend": "2028-01-09", "notice": 30, "ins": "Pragati Life", "policy": "PL-EMP-2033", "cov": 800000, "iexp": "2026-12-15"},
    {"id": 4, "name": "Mizanur Rahman", "designation": "Project Manager", "dept": "Management", "phone": "01777779999", "email": "mizan@mars.com", "join": "2020-09-01", "salary": 120000, "status": "active", "ctype": "Permanent", "cstart": "2020-09-01", "cend": "2026-07-05", "notice": 90, "ins": "Green Delta Insurance", "policy": "GD-EMP-1004", "cov": 2500000, "iexp": "2026-08-01"},
    {"id": 5, "name": "Tanvir Ahmed", "designation": "Civil Engineer", "dept": "Construction", "phone": "01799991111", "email": "tanvir@mars.com", "join": "2022-07-20", "salary": 70000, "status": "active", "ctype": "Permanent", "cstart": "2022-07-20", "cend": "2027-07-19", "notice": 30, "ins": "Pragati Life", "policy": "PL-EMP-2035", "cov": 1000000, "iexp": "2026-09-30"},
    {"id": 6, "name": "Shahana Parvin", "designation": "HR Executive", "dept": "HR", "phone": "01744446666", "email": "shahana@mars.com", "join": "2024-02-01", "salary": 45000, "status": "probation", "ctype": "Contractual", "cstart": "2024-02-01", "cend": "2026-08-01", "notice": 15, "ins": "Pragati Life", "policy": "PL-EMP-2036", "cov": 500000, "iexp": "2026-08-01"},
    {"id": 7, "name": "Nazmul Huda", "designation": "Project Manager", "dept": "Construction", "phone": "01810112233", "email": "nazmul@mars.com", "join": "2021-11-05", "salary": 115000, "status": "active", "ctype": "Permanent", "cstart": "2021-11-05", "cend": "2028-11-04", "notice": 90, "ins": "Green Delta Insurance", "policy": "GD-EMP-1007", "cov": 2000000, "iexp": "2027-01-15"},
    {"id": 8, "name": "Sultana Razia", "designation": "HR Manager", "dept": "HR", "phone": "01710223344", "email": "sultana@mars.com", "join": "2019-04-22", "salary": 95000, "status": "active", "ctype": "Permanent", "cstart": "2019-04-22", "cend": "2027-04-21", "notice": 60, "ins": "Green Delta Insurance", "policy": "GD-EMP-1008", "cov": 1800000, "iexp": "2026-11-30"},
    {"id": 9, "name": "Jahir Uddin", "designation": "Accountant", "dept": "Finance", "phone": "01910334455", "email": "jahir@mars.com", "join": "2023-08-14", "salary": 52000, "status": "active", "ctype": "Permanent", "cstart": "2023-08-14", "cend": "2026-12-31", "notice": 30, "ins": "Pragati Life", "policy": "PL-EMP-2039", "cov": 700000, "iexp": "2026-10-31"},
    {"id": 10, "name": "Faruk Hossain", "designation": "Site Supervisor", "dept": "Construction", "phone": "01710445566", "email": "faruk@mars.com", "join": "2024-01-15", "salary": 42000, "status": "active", "ctype": "Contractual", "cstart": "2024-01-15", "cend": "2026-12-31", "notice": 15, "ins": "Pragati Life", "policy": "PL-EMP-2040", "cov": 500000, "iexp": "2026-07-08"},
    {"id": 11, "name": "Morshed Alam", "designation": "Legal Officer", "dept": "Management", "phone": "01810556677", "email": "morshed@mars.com", "join": "2022-05-30", "salary": 68000, "status": "active", "ctype": "Permanent", "cstart": "2022-05-30", "cend": "2027-05-29", "notice": 60, "ins": "Green Delta Insurance", "policy": "GD-EMP-1011", "cov": 1200000, "iexp": "2026-09-15"},
    {"id": 12, "name": "Shahnaz Parvin", "designation": "Marketing Executive", "dept": "Sales", "phone": "01710667788", "email": "shahnaz@mars.com", "join": "2024-03-10", "salary": 48000, "status": "on-leave", "ctype": "Contractual", "cstart": "2024-03-10", "cend": "2026-06-30", "notice": 15, "ins": "Pragati Life", "policy": "PL-EMP-2042", "cov": 500000, "iexp": "2026-06-25"},
]

LEAVES = [
    {"id": "LV-001", "emp": 12, "type": "Annual", "from": "2026-07-28", "to": "2026-07-30", "status": "Approved", "reason": "Family trip to Cox's Bazar", "approver": "Sultana Razia"},
    {"id": "LV-002", "emp": 6, "type": "Sick", "from": "2026-07-27", "to": "2026-07-28", "status": "Pending", "reason": "Viral fever — medical certificate attached"},
    {"id": "LV-003", "emp": 2, "type": "Casual", "from": "2026-08-02", "to": "2026-08-02", "status": "Pending", "reason": "Personal work at bank"},
    {"id": "LV-004", "emp": 9, "type": "Festival", "from": "2026-07-30", "to": "2026-08-01", "status": "Approved", "reason": "Eid-ul-Adha travel to hometown", "approver": "Sultana Razia"},
    {"id": "LV-005", "emp": 5, "type": "Annual", "from": "2026-08-10", "to": "2026-08-14", "status": "Pending", "reason": "Annual vacation — advance notice given"},
    {"id": "LV-006", "emp": 10, "type": "Sick", "from": "2026-07-25", "to": "2026-07-26", "status": "Rejected", "reason": "No medical certificate — resubmit"},
    {"id": "LV-007", "emp": 3, "type": "Casual", "from": "2026-08-05", "to": "2026-08-06", "status": "Pending", "reason": "Sister's wedding"},
    {"id": "LV-008", "emp": 7, "type": "Annual", "from": "2026-07-20", "to": "2026-07-24", "status": "Approved", "reason": "Post-project break after Muktodhara handover", "approver": "Sultana Razia"},
]

SHIFTS = [
    {"code": "SFT-01", "name": "General", "start": "09:00", "end": "18:00", "ot": 1},
    {"code": "SFT-02", "name": "Morning", "start": "07:00", "end": "15:00", "ot": 0},
    {"code": "SFT-03", "name": "Evening", "start": "15:00", "end": "23:00", "ot": 0},
    {"code": "SFT-04", "name": "Site 7–4", "start": "07:00", "end": "16:00", "ot": 1},
]


def _company():
    return frappe.db.get_value("Company", {}, "name") or "Mars Constact"


def seed_hr():
    # shifts first
    for s in SHIFTS:
        if not frappe.db.exists("REM Shift", {"shift_code": s["code"]}):
            d = frappe.new_doc("REM Shift")
            d.shift_code = s["code"]
            d.shift_name = s["name"]
            d.start_time = s["start"]
            d.end_time = s["end"]
            d.overtime = s["ot"]
            d.save(ignore_permissions=True)
    # employees
    emp_map = {}
    for e in EMPLOYEES:
        name = frappe.db.get_value("Employee", {"custom_rem_ref": str(e["id"])}, "name")
        if name:
            emp_map[e["id"]] = name
            continue
        d = frappe.new_doc("Employee")
        d.first_name = e["name"].split(" ")[0]
        if " " in e["name"]:
            d.last_name = e["name"].split(" ", 1)[1]
        d.status = "Active"
        d.company = _company()
        d.designation = _resolve("Designation", "designation_name", e["designation"])
        d.department = _resolve("Department", "department_name", e["dept"])
        d.cell_number = e["phone"]
        d.personal_email = e["email"]
        d.date_of_joining = e["join"]
        d.ctc = e["salary"]
        d.custom_rem_ref = str(e["id"])
        d.custom_contract_type = e["ctype"]
        d.custom_contract_start = e["cstart"]
        d.custom_contract_end = e["cend"]
        d.custom_notice_days = e["notice"]
        d.custom_insurance_provider = e["ins"]
        d.custom_insurance_policy = e["policy"]
        d.custom_insurance_coverage = e["cov"]
        d.custom_insurance_expiry = e["iexp"]
        d.flags.ignore_mandatory = True
        d.save(ignore_permissions=True)
        emp_map[e["id"]] = d.name
    # leaves
    for lv in LEAVES:
        emp = emp_map.get(lv["emp"], "")
        if not emp:
            continue
        if not frappe.db.exists("REM Leave", {"employee": emp, "from_date": lv["from"], "leave_type": lv["type"]}):
            d = frappe.new_doc("REM Leave")
            d.employee = emp
            d.leave_type = lv["type"]
            d.from_date = lv["from"]
            d.to_date = lv["to"]
            d.status = lv["status"]
            d.reason = lv["reason"]
            d.approver = lv.get("approver", "")
            d.save(ignore_permissions=True)
    # attendance: last 7 days per employee
    today = date.today()
    pool = ["Present", "Present", "Present", "Late", "Absent", "Leave", "Present"]
    n = 0
    for eid, emp in emp_map.items():
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            wd = d.weekday()
            if wd >= 5:
                status = "Weekend"
            elif eid == 12:  # on-leave
                status = "Leave"
            else:
                status = pool[(eid * 5 + i * 2) % len(pool)]
            if frappe.db.exists("REM Attendance", {"employee": emp, "attendance_date": str(d)}):
                continue
            a = frappe.new_doc("REM Attendance")
            a.employee = emp
            a.attendance_date = str(d)
            a.status = status
            if status == "Present":
                a.in_time = "09:0" + str((eid + i) % 10)
                a.out_time = "18:00"
                a.shift = "SFT-01"
            a.save(ignore_permissions=True)
            n += 1
    frappe.db.commit()
    print(json.dumps({
        "employees": len(emp_map),
        "leaves": frappe.db.count("REM Leave"),
        "attendance": frappe.db.count("REM Attendance"),
        "shifts": frappe.db.count("REM Shift"),
    }))


def _resolve(doctype, field, value):
    name = frappe.db.get_value(doctype, {field: value}, "name")
    if name:
        return name
    d = frappe.new_doc(doctype)
    d.set(field, str(value)[:140])
    d.flags.ignore_mandatory = True
    d.save(ignore_permissions=True)
    return d.name
