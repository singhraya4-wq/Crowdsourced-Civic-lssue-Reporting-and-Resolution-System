from flask import Flask, render_template, request, jsonify, session, redirect
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "secret123"

# ------------------ USERS ------------------
# Predefined admin + dynamic users
users = {
    "admin": "admin123"
}

# ------------------ SAMPLE DATA ------------------

titles = ["Pothole", "Streetlight issue", "Garbage overflow", "Water leakage"]
locations = ["Rajiv Chowk", "Saket", "Dwarka", "Rohini"]
categories = ["Road", "Electricity", "Sanitation", "Water"]
priorities = ["Low", "Medium", "High"]

issues = []

for i in range(1, 31):
    issues.append({
        "id": i,
        "title": random.choice(titles),
        "location": "Delhi - " + random.choice(locations),
        "category": random.choice(categories),
        "priority": random.choice(priorities),
        "status": random.choice(["Pending", "Resolved"]),
        "assigned_to": "Municipal Dept",
        "timestamp": (datetime.now() - timedelta(days=random.randint(0,5))).strftime("%Y-%m-%d %H:%M"),
        "user": "demo"
    })

# ------------------ ROUTES ------------------

@app.route("/")
def login():
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html")


@app.route("/user")
def user():
    if "user" not in session:
        return redirect("/")
    return render_template("user.html")


@app.route("/admin")
def admin():
    if "user" not in session:
        return redirect("/")
    return render_template("admin.html")


@app.route("/myreports")
def myreports():
    if "user" not in session:
        return redirect("/")
    return render_template("myreports.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ------------------ API ------------------

# LOGIN
@app.route("/api/login", methods=["POST"])
def login_api():
    data = request.json

    username = data.get("username")
    password = data.get("password")

    if username in users:
        if users[username] == password:
            session["user"] = username
            return jsonify({"msg": "success"})
        else:
            return jsonify({"msg": "wrong password"})
    else:
        # create new user
        users[username] = password
        session["user"] = username
        return jsonify({"msg": "success"})


# GET ALL ISSUES (ADMIN / DASHBOARD)
@app.route("/api/issues")
def get_issues():
    return jsonify(issues)


# GET USER-SPECIFIC ISSUES
@app.route("/api/myissues")
def myissues():
    user = session.get("user")
    user_issues = [i for i in issues if i.get("user") == user]
    return jsonify(user_issues)


# REPORT ISSUE
@app.route("/api/report", methods=["POST"])
def report():
    data = request.json

    new_issue = {
        "id": len(issues) + 1,
        "title": data["title"],
        "location": data["location"],
        "category": data["category"],
        "priority": data["priority"],
        "status": "Pending",
        "assigned_to": "Not Assigned",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "user": session.get("user")   # 🔥 IMPORTANT
    }

    issues.append(new_issue)

    return jsonify({"msg": "submitted"})


# UPDATE ISSUE (ADMIN)
@app.route("/api/update", methods=["POST"])
def update():
    data = request.json

    for i in issues:
        if i["id"] == data["id"]:
            i["status"] = data["status"]
            i["assigned_to"] = data.get("assigned_to", "Dept")

    return jsonify({"msg": "updated"})


# ------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)