import gradio as gr
import json
import uuid
import pandas as pd
import random
import os
import plotly.express as px

# ------------------ FILES ------------------
DATA_FILE = "data.json"
USER_FILE = "users.json"

# ------------------ PRELOAD DATA ------------------
users = ["Raya","Rahul","Neha","Amit","Karan","Simran","Ananya","Vikram","Priya","Aditya",
         "Sakshi","Rohan","Nikhil","Tanvi","Meera","Harsh","Ishita","Varun","Sonia","Akash",
         "Pooja","Kunal","Shreya","Arjun","Divya","Tanya","Yash","Ankit","Naina","Ritika",
         "Sahil","Rhea","Dev","Neel","Maya","Ira","Kabir","Sanya","Raghav","Tara"]

if not os.path.exists(DATA_FILE):
    categories = ["Water","Road","Electricity","Other"]
    severities = ["Low","Medium","High"]
    statuses = ["Pending","Resolved"]
    locations = ["Dwarka Sector {}", "Rohini Sector {}", "Lajpat Nagar","Janakpuri","Uttam Nagar",
                 "Connaught Place","Pitampura","Saket","Karol Bagh","Greater Kailash"]
    data = []
    for i in range(1, 501):
        user = random.choice(users)
        problem = f"{random.choice(['Leakage','Pothole','Street light','Garbage','Pipeline','Road damage','Water contamination','Power cut','Traffic signal'])} at {random.choice(['main road','park','residential area','market','junction'])}"
        location = random.choice(locations).format(random.randint(1,25) if "{}" in locations[0] else "")
        issue_type = random.choice(categories)
        severity = random.choice(severities)
        status = random.choice(statuses)
        issue_id = f"{i:04d}{uuid.uuid4().hex[:4].upper()}"
        data.append({
            "id": issue_id,
            "user": user,
            "problem": problem,
            "location": location,
            "type": issue_type,
            "severity": severity,
            "status": status
        })
    with open(DATA_FILE, "w") as f:
        json.dump(data,f,indent=4)

if not os.path.exists(USER_FILE):
    save_users = [{"username": u} for u in users]
    with open(USER_FILE,"w") as f:
        json.dump(save_users,f,indent=4)

# ------------------ UTILS ------------------
def load_json(file):
    with open(file,"r") as f:
        return json.load(f)
def save_json(file,data):
    with open(file,"w") as f:
        json.dump(data,f,indent=4)

# ------------------ LOGIN ------------------
def login(username,password):
    if username=="admin" and password=="admin123":
        return "admin", f"Welcome Admin 👑"
    users_data = load_json(USER_FILE)
    if username not in [u["username"] for u in users_data]:
        users_data.append({"username":username})
        save_json(USER_FILE, users_data)
    return "user", f"Welcome {username} 👤"

# ------------------ DASHBOARD ------------------
def get_dashboard_data(user=None):
    df = pd.DataFrame(load_json(DATA_FILE))
    if user:
        df_user = df[df["user"]==user]
    else:
        df_user = df
    total = len(df_user)
    pending = len(df_user[df_user["status"]=="Pending"])
    resolved = len(df_user[df_user["status"]=="Resolved"])
    cat_counts = df_user["type"].value_counts().to_dict()
    severity_counts = df_user["severity"].value_counts().to_dict()
    return df_user, total, pending, resolved, cat_counts, severity_counts

def plot_graphs(df):
    if df.empty:
        return None,None,None
    fig_cat = px.pie(df,names="type",title="Reports by Category",color_discrete_sequence=px.colors.qualitative.Bold)
    fig_status = px.pie(df,names="status",title="Pending vs Resolved",color_discrete_sequence=px.colors.qualitative.Set2)
    fig_sev = px.pie(df,names="severity",title="Severity Distribution",color_discrete_sequence=px.colors.qualitative.Set1)
    return fig_cat,fig_status,fig_sev

# ------------------ SUBMIT & RESOLVE ------------------
def submit_issue(user,problem,location,issue_type,severity):
    data = load_json(DATA_FILE)
    issue_id = str(uuid.uuid4())[:8]
    new_issue = {
        "id": issue_id,
        "user": user,
        "problem": problem,
        "location": location,
        "type": issue_type,
        "severity": severity,
        "status": "Pending"
    }
    data.append(new_issue)
    save_json(DATA_FILE,data)
    return f"✅ Your report has been submitted! Issue ID: {issue_id}"

def resolve_issue(issue_id):
    data = load_json(DATA_FILE)
    found=False
    for d in data:
        if d["id"]==issue_id:
            d["status"]="Resolved"
            found=True
    save_json(DATA_FILE,data)
    return "✅ Updated Successfully" if found else "❌ Issue ID not found"

# ------------------ APP ------------------
with gr.Blocks() as app:
    user_state = gr.State()
    role_state = gr.State()

    # ---------- LOGIN PAGE ----------
    with gr.Column() as login_page:
        gr.Markdown("<h1 style='text-align:center;color:white'>🔐 Civic Issue Reporting System</h1>")
        username = gr.Textbox(label="Username",placeholder="Enter username")
        password = gr.Textbox(label="Password", type="password", placeholder="Enter password")
        login_msg = gr.Markdown()
        login_btn = gr.Button("Login")

    # ---------- MAIN PAGE ----------
    with gr.Row() as main_page:
        main_page.visible=False

        # Sidebar
        with gr.Column(scale=1):
            nav = gr.Radio([],label="Navigation")
            logout_btn = gr.Button("Logout")

        # Content
        with gr.Column(scale=4):
            content_text = gr.Markdown()
            content_table = gr.Dataframe()
            # Admin Graphs
            fig_cat = gr.Plot()
            fig_status = gr.Plot()
            fig_sev = gr.Plot()
            # User Submit Panel
            problem = gr.Textbox(label="Problem")
            location = gr.Textbox(label="Location")
            issue_type = gr.Dropdown(["Water","Road","Electricity","Other"],label="Type")
            severity = gr.Dropdown(["Low","Medium","High"],label="Severity")
            submit_btn = gr.Button("Submit")
            submit_msg = gr.Markdown()
            # Admin Resolve Panel
            issue_id = gr.Textbox(label="Enter Issue ID to Resolve")
            resolve_btn = gr.Button("Mark Resolved")
            resolve_msg = gr.Markdown()

    # ---------- LOGIN ----------
    def handle_login(u,p):
        role,msg = login(u,p)
        if role=="admin":
            nav_choices=["Overview","Resolve Issue"]
        else:
            nav_choices=["Overall","Submit Issue"]
        return gr.update(visible=False),gr.update(visible=True),u,role,msg,gr.update(choices=nav_choices,value=nav_choices[0])

    login_btn.click(handle_login,
                     inputs=[username,password],
                     outputs=[login_page,main_page,user_state,role_state,login_msg,nav])

    # ---------- LOGOUT ----------
    def handle_logout():
        return gr.update(visible=True),gr.update(visible=False)
    logout_btn.click(handle_logout,outputs=[login_page,main_page])

    # ---------- NAVIGATION ----------
    def show_panel(selection,user,role):
        df,total,pending,resolved,cat_counts,sev_counts = get_dashboard_data(user if role=="user" else None)
        content_text_val = f"📊 Total: {total}  ⏳ Pending: {pending}  ✅ Resolved: {resolved}"

        panels_visibility = {
            content_text: True, content_table: True,
            fig_cat: False, fig_status: False, fig_sev: False,
            problem: False, location: False, issue_type: False, severity: False, submit_btn: False, submit_msg: False,
            issue_id: False, resolve_btn: False, resolve_msg: False
        }

        fig_c = fig_s = fig_se = None

        if role=="admin":
            if selection=="Overview":
                fig_c,fig_s,fig_se = plot_graphs(df)
                panels_visibility[fig_cat]=True
                panels_visibility[fig_status]=True
                panels_visibility[fig_sev]=True
            elif selection=="Resolve Issue":
                panels_visibility[issue_id]=True
                panels_visibility[resolve_btn]=True
                panels_visibility[resolve_msg]=True

        if role=="user":
            if selection=="Overall":
                pass  # only table
            elif selection=="Submit Issue":
                panels_visibility[problem]=True
                panels_visibility[location]=True
                panels_visibility[issue_type]=True
                panels_visibility[severity]=True
                panels_visibility[submit_btn]=True
                panels_visibility[submit_msg]=True

        return (
            gr.update(value=content_text_val,visible=panels_visibility[content_text]),
            gr.update(value=df,visible=panels_visibility[content_table]),
            gr.update(value=fig_c,visible=panels_visibility[fig_cat]),
            gr.update(value=fig_s,visible=panels_visibility[fig_status]),
            gr.update(value=fig_se,visible=panels_visibility[fig_sev]),
            gr.update(visible=panels_visibility[problem]),
            gr.update(visible=panels_visibility[location]),
            gr.update(visible=panels_visibility[issue_type]),
            gr.update(visible=panels_visibility[severity]),
            gr.update(visible=panels_visibility[submit_btn]),
            gr.update(visible=panels_visibility[submit_msg]),
            gr.update(visible=panels_visibility[issue_id]),
            gr.update(visible=panels_visibility[resolve_btn]),
            gr.update(visible=panels_visibility[resolve_msg])
        )

    nav.change(show_panel,inputs=[nav,user_state,role_state],
               outputs=[content_text,content_table,fig_cat,fig_status,fig_sev,
                        problem,location,issue_type,severity,submit_btn,submit_msg,
                        issue_id,resolve_btn,resolve_msg])

    submit_btn.click(submit_issue,inputs=[user_state,problem,location,issue_type,severity],
                     outputs=submit_msg)
    resolve_btn.click(resolve_issue,inputs=issue_id,outputs=resolve_msg)

# ---------- LAUNCH ----------
app.launch(theme=gr.themes.Soft(), css="""
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
body { background-color:#0f0f0f; color:white; font-family:'Roboto',sans-serif;}
.sidebar { background-color:#1f1f1f; padding:15px; border-radius:8px;}
button { border-radius: 8px !important; font-weight:600; padding:8px 12px !important; margin:5px 0; border:none; cursor:pointer; transition:transform 0.15s;}
button:hover { transform: scale(1.05);}
.submit-btn { background-color:#1E90FF; color:white;}
.login-btn { background-color:#32CD32; color:white;}
.logout-btn { background-color:#FF4500; color:white;}
.resolve-btn { background-color:#FFD700; color:black;}
.gr-dataframe th { background-color:#2c2c2c !important; color:#ffffff !important; font-weight:500;}
.gr-dataframe td { background-color:#1a1a1a !important; color:#ffffff !important;}
.gr-dataframe tr:hover td { background-color:#333333 !important;}
.gr-markdown { line-height:1.5; margin-bottom:10px;}
.gr-plot { background-color:#1a1a1a; border-radius:8px; padding:5px;}
input[type=text], input[type=password], select { background-color:#1a1a1a !important; color:white !important; border: 1px solid #444 !important; border-radius:6px !important; padding:6px 8px !important;}
input[type=text]:hover, input[type=password]:hover, select:hover { border-color:#32CD32 !important;}
""")