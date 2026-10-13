import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import URL, text
from sqlalchemy.exc import IntegrityError, OperationalError

# Load the database settings from .env
load_dotenv()

# Create the Flask website
app = Flask(__name__)

# Allow the application to update while the server is running
app.config["DEBUG"] = True

app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

# Tell SQLAlchemy which database to connect to
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

db = SQLAlchemy(app)

# Check database connection
try:
    with app.app_context():
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT DATABASE();"))
            print("Connected to database:", result.scalar())

except OperationalError:
    raise SystemExit("Database connection failed. Stopping app.")


# -----------------------------------
# ----------DATABASE MODELS----------
# -----------------------------------

class Employee(db.Model):
    __tablename__ = "employee"

    employee_id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    phone_number = db.Column(db.String(30))
    job_title = db.Column(db.String(100), nullable=False)

    password_hash = db.Column(db.String(255))

    active = db.Column(db.Boolean, nullable=False, default=True)
    admin = db.Column(db.Boolean, nullable=False, default=False)


class Tool(db.Model):
    __tablename__ = "tool"

    asset_id = db.Column(db.Integer, primary_key=True)

    tool_name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    description = db.Column(db.Text)

    purchase_date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Numeric(12, 2), nullable=False)

    asset_tag = db.Column(db.String(100), unique=True, nullable=False)
    serial_number = db.Column(db.String(150))

    status = db.Column(
        db.Enum(
            "Available",
            "Assigned",
            "Missing",
            "Damaged",
            "Under Repair"
        ),
        nullable=False
    )

    condition = db.Column(
        db.Enum("New", "Good", "Fair", "Poor", "Unknown"),
        nullable=False
    )

    notes = db.Column(db.Text)

    active_assignment = db.relationship(
        "Assignment",
        primaryjoin="and_(Tool.asset_id == Assignment.asset_id, Assignment.active == True)",
        uselist=False,
        viewonly=True
    )


# Tool checkout and return records
class Assignment(db.Model):
    __tablename__ = "assignment"

    assignment_id = db.Column(db.Integer, primary_key=True)

    asset_id = db.Column(
        db.Integer,
        db.ForeignKey("tool.asset_id"),
        nullable=False
    )

    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employee.employee_id"),
        nullable=False
    )

    job_vehicle_number = db.Column(db.String(150))

    date_assigned = db.Column(db.DateTime, nullable=False)
    expected_return_date = db.Column(db.DateTime)
    actual_return_date = db.Column(db.DateTime)

    condition_when_assigned = db.Column(
        db.Enum("New", "Good", "Fair", "Poor", "Unknown"),
        nullable=False
    )

    condition_when_returned = db.Column(
        db.Enum("New", "Good", "Fair", "Poor", "Unknown")
    )

    missing_reported_date = db.Column(db.DateTime)
    missing_resolved_date = db.Column(db.DateTime)

    notes = db.Column(db.Text)

    active = db.Column(db.Boolean, nullable=False, default=True)

    tool = db.relationship("Tool", foreign_keys=[asset_id])
    employee = db.relationship("Employee", foreign_keys=[employee_id])


# -----------------------------------
# ----------HELPER FUNCTIONS---------
# -----------------------------------

def format_phone(phone):
    if not phone:
        return None

    if any(character not in "0123456789-" for character in phone):
        raise ValueError("Phone number can only contain digits and dashes.")

    digits = phone.replace("-", "")

    if len(digits) != 10:
        raise ValueError("Phone number must contain exactly 10 digits.")

    return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"


# -----------------------------------
# ----------LOGIN--------------------
# -----------------------------------

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        mydb = db.engine.raw_connection()

        try:
            cursor = mydb.cursor()

            try:
                query = """
                    SELECT *
                    FROM employee
                    WHERE email = %s
                    AND password_hash = %s
                    AND admin = True
                """

                cursor.execute(query, (username, password))
                admin = cursor.fetchone()

            finally:
                cursor.close()

        finally:
            mydb.close()

        if admin:
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials. Please try again.", "error")
            return render_template("login.html")

    return render_template("login.html")


# -----------------------------------
# ----------DASHBOARD----------------
# -----------------------------------

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# -----------------------------------
# ----------EMPLOYEES----------------
# -----------------------------------

@app.route("/employees")
def employees():
    employee_list = db.session.execute(
        db.select(Employee).order_by(Employee.name)
    ).scalars().all()

    return render_template(
        "employees.html",
        employees=employee_list
    )


@app.route("/employees/add", methods=["GET", "POST"])
def add_employee():
    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone_number", "").strip()
        job_title = request.form.get("job_title", "").strip()

        if not name or not email or not job_title:
            error = "Name, email, and job title are required."
        else:
            try:
                phone = format_phone(phone)
            except ValueError as message:
                error = str(message)
            else:
                employee = Employee(
                    name=name,
                    email=email,
                    phone_number=phone or None,
                    job_title=job_title,
                    active=True,
                    admin=False,
                    password_hash=None
                )

                try:
                    db.session.add(employee)
                    db.session.commit()

                except IntegrityError:
                    db.session.rollback()
                    error = "Could not save. That email may already be in use."

                else:
                    return redirect(url_for("employees"))

    return render_template(
        "add_employee.html",
        error=error
    )


@app.route("/employees/<int:employee_id>/edit", methods=["GET", "POST"])
def edit_employee(employee_id):
    employee = db.get_or_404(Employee, employee_id)
    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone_number", "").strip()
        job_title = request.form.get("job_title", "").strip()

        admin = request.form.get("admin") == "1"
        active = request.form.get("active") == "1"

        if not name or not email or not job_title:
            error = "Name, email, and job title are required."
        else:
            try:
                phone = format_phone(phone)
            except ValueError as message:
                error = str(message)
            else:
                employee.name = name
                employee.email = email
                employee.phone_number = phone or None
                employee.job_title = job_title
                employee.admin = admin
                employee.active = active

                try:
                    db.session.commit()

                except IntegrityError:
                    db.session.rollback()
                    error = "Could not save. That email may already be in use."

                else:
                    return redirect(url_for("employees"))

    return render_template(
        "edit_employee.html",
        employee=employee,
        error=error
    )


# -----------------------------------
# ----------TOOL INVENTORY-----------
# -----------------------------------

@app.route("/tools")
def tool_inventory():
    tool_list = db.session.execute(
        db.select(Tool).order_by(Tool.asset_tag)
    ).scalars().all()

    return render_template(
        "tool_inventory.html",
        tools=tool_list
    )


@app.route("/tools/add")
def add_tool():
    return render_template("add_tool.html")


@app.route("/tools/<int:asset_id>")
def tool_details(asset_id):
    tool = db.get_or_404(Tool, asset_id)
    return "Placeholder"


# -----------------------------------
# ----------TOOL CATEGORIES----------
# -----------------------------------

@app.route("/tool_types")
def tool_types():
    categories = db.session.execute(
        db.select(Tool.category).distinct()
    ).scalars().all()

    coded_limits = {
        "Vacuum Pumps": 1,
        "Recovery Machines": 2,
        "Hand Tools": 5
    }

    tool_type_summary = []

    for category in categories:
        available_count = Tool.query.filter_by(
            category=category,
            status="Available"
        ).count()

        limit = coded_limits.get(category, 0)
        is_low = available_count <= limit

        tool_type_summary.append({
            "category": category,
            "available_count": available_count,
            "warning_limit": limit,
            "is_low": is_low
        })

    return render_template(
        "tool_types.html",
        tool_types=tool_type_summary
    )


# -----------------------------------
# ----------TOOL RETURNS-------------
# -----------------------------------

# Show all tools that are currently checked out
@app.route("/tools/returns")
def tool_returns():
    assignments = db.session.execute(
        db.select(Assignment)
        .where(
            Assignment.active.is_(True),
            Assignment.actual_return_date.is_(None)
        )
        .order_by(Assignment.date_assigned.desc())
    ).scalars().all()

    return render_template(
        "tool_returns.html",
        assignments=assignments
    )


# Process a returned tool
@app.route("/tools/returns/<int:assignment_id>", methods=["POST"])
def return_tool(assignment_id):
    condition = request.form.get("condition", "").strip()
    notes = request.form.get("notes", "").strip()

    valid_conditions = ["New", "Good", "Fair", "Poor", "Unknown"]

    if condition not in valid_conditions:
        flash("Please select a valid condition.", "error")
        return redirect(url_for("tool_returns"))

    try:
        # Lock the tool first so two returns cannot update it together
        assignment_info = db.session.execute(
            db.select(Assignment.asset_id)
            .where(Assignment.assignment_id == assignment_id)
        ).scalar_one_or_none()

        if assignment_info is None:
            flash("Assignment not found.", "error")
            return redirect(url_for("tool_returns"))

        tool = db.session.execute(
            db.select(Tool)
            .where(Tool.asset_id == assignment_info)
            .with_for_update()
        ).scalar_one_or_none()

        if tool is None:
            db.session.rollback()
            flash("Tool not found.", "error")
            return redirect(url_for("tool_returns"))

        assignment = db.session.execute(
            db.select(Assignment)
            .where(Assignment.assignment_id == assignment_id)
            .with_for_update()
        ).scalar_one_or_none()

        if (
            assignment is None
            or not assignment.active
            or assignment.actual_return_date is not None
        ):
            db.session.rollback()
            flash("This tool has already been returned.", "error")
            return redirect(url_for("tool_returns"))

        assignment.actual_return_date = (
            datetime.now(timezone.utc).replace(tzinfo=None)
        )

        assignment.condition_when_returned = condition
        assignment.active = False

        if notes:
            if assignment.notes:
                assignment.notes += "\nReturn: " + notes
            else:
                assignment.notes = "Return: " + notes

        tool.condition = condition

        # Keep damaged tools out of available inventory
        if condition == "Poor":
            tool.status = "Damaged"
        else:
            tool.status = "Available"

        db.session.commit()

        flash("Tool returned successfully.", "success")

    except Exception:
        db.session.rollback()
        app.logger.exception("Error returning tool")
        flash("Could not return tool. Please try again.", "error")

    return redirect(url_for("tool_returns"))


# -----------------------------------
# ----------START APPLICATION--------
# -----------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
