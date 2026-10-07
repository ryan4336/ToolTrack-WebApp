import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import URL, text


# Load the database settings from .env
load_dotenv()

# Create the Flask website
app = Flask(__name__)

# Tell SQLAlchemy which database to connect to
# URL.create handles special characters in the password correctly
app.config["SQLALCHEMY_DATABASE_URI"] = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME")
)

# Use the Aiven certificate to verify the database server
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "connect_args": {
        "ssl_ca": os.getenv("DB_SSL_CA"),
        "ssl_verify_cert": True,
        "ssl_verify_identity": True
    }
}

# Set up SQLAlchemy for this Flask app
db = SQLAlchemy(app)

# Check that it can connect when the app starts
with app.app_context():
    with db.engine.connect() as connection:
        result = connection.execute(text("SELECT DATABASE();"))
        print("Connected to database:", result.scalar())


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