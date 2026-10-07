from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


# Show the login page when someone first opens the website
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    # Temporarily send every submitted login directly to the dashboard
    # Authentication will be added later
    if request.method == "POST":
        return redirect(url_for("dashboard"))

    return render_template("login.html")


# Display the dashboard page
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")