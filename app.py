from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
import cx_Oracle

app = Flask(__name__)
app.secret_key = "super_secret"

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, uid, username, password, role):
        self.id = uid
        self.username = username
        self.password = password
        self.role = role

def get_db():
    dsn = cx_Oracle.makedsn("localhost", 1521, "ORCL")
    return cx_Oracle.connect(user='sys', password='Student27', dsn)

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password, role FROM users WHERE id = :id", {"id": user_id})
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return User(*row)
    return None

def role_required(role):
    def decorator(f):
        def wrapper(*args, **kwargs):
            if current_user.role != role:
                flash("Access restricted!", "warning")
                return redirect(url_for("dashboard"))
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, username, password, role FROM users WHERE username = :u", {"u": username})
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row and check_password_hash(row[2], password):
            user = User(*row)
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials!", "danger")

    return render_template("index.html", page="login")

@app.route("/")
@login_required
def dashboard():
    conn = get_db()
    cur = conn.cursor()

    if current_user.role == "hr":
        cur.execute("SELECT employeeid, name, department FROM employee ORDER BY employeeid")
        data = cur.fetchall()
        return render_template("index.html", page="hr", employees=data)

    elif current_user.role == "finance":
        cur.execute("SELECT employeeid, name, salary FROM employee ORDER BY employeeid")
        data = cur.fetchall()
        return render_template("index.html", page="finance", employees=data)

    else:  # employee
        cur.execute("SELECT employeeid, name, department, salary FROM employee WHERE employeeid = :id",
                    {"id": current_user.id})
        data = cur.fetchone()
        return render_template("index.html", page="employee", employee=data)

@app.route("/process/<int:emp_id>")
@login_required
@role_required("finance")
def process(emp_id):
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.callproc("payroll_pkg.calculate_salary", [emp_id])
        conn.commit()
        flash("Payroll processed!", "success")
    except Exception as e:
        flash(str(e), "danger")

    cur.close()
    conn.close()
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)


