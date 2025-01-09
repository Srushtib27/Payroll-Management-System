from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import cx_Oracle

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    try:
        dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
        conn = cx_Oracle.connect(user='sys', password='Student27', dsn=dsn_tns, mode=cx_Oracle.SYSDBA)
        return conn
    except cx_Oracle.DatabaseError as e:
        print(f"Database connection failed: {e}")
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password, role FROM users WHERE username = :1", [username])
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user and check_password_hash(user[0], password):
                session['user_type'] = user[1]
                flash("Logged in successfully", "success")
                return redirect(url_for('index'))
            else:
                flash("Invalid username or password", "danger")
        else:
            flash("Database connection failed", "danger")

    return render_template('main.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for('login'))

@app.route('/')
def index():
    user_type = session.get('user_type')
    
    if not user_type:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed", "danger")
        return redirect(url_for('login'))

    cursor = conn.cursor()
    
    if user_type == 'hr':
        cursor.execute("SELECT EmployeeID, Name, Department FROM Employee")
        all_employees = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('main.html', user_type='hr', employees=all_employees)

    elif user_type == 'accountant':
        cursor.execute("SELECT EmployeeID, Name, Salary FROM Employee")
        all_employees = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('main.html', user_type='accountant', employees=all_employees)

    elif user_type == 'employee':
        emp_id = request.args.get('id')
        cursor.execute("SELECT EmployeeID, Name, Department, Salary FROM Employee WHERE EmployeeID = :1", [emp_id])
        employee = cursor.fetchone()
        cursor.close()
        conn.close()

        if employee:
            return render_template('main.html', user_type='employee', employee=employee)
        else:
            flash(f"Employee with ID {emp_id} not found", "danger")
            return render_template('main.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
