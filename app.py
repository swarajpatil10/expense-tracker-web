from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import date
from dotenv import load_dotenv
import os

load_dotenv()

import psycopg2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'x7Kp9mQ2vL4nR8wZ1tY6bH3jF5cA0dE'

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="expensedb",
        user="postgres",
        password=os.environ.get('DB_PASSWORD'),
        port=5432
    )


class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return User(id=row[0], username=row[1])
    return None


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
        conn.commit()
        cur.close()
        conn.close()

        flash('Account created! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, password_hash FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row and bcrypt.check_password_hash(row[2], password):
            user = User(id=row[0], username=row[1])
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/")
@login_required
def home():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, amount, category, description, date FROM expenses WHERE user_id = %s ORDER BY id",
        (current_user.id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    expenses = []
    for row in rows:
        expenses.append({
            "id": row[0],
            "amount": row[1],
            "category": row[2],
            "description": row[3],
            "date": row[4]
        })

    total = sum(e["amount"] for e in expenses)
    return render_template("home.html", expenses=expenses, total=total)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        amount = float(request.form["amount"])
        category = request.form["category"]
        description = request.form["description"]
        today = date.today()

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO expenses (amount, category, description, date, user_id) VALUES (%s, %s, %s, %s, %s)",
            (amount, category, description, today, current_user.id)
        )
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("home"))
    return render_template("add.html")


@app.route("/delete/<int:expense_id>")
@login_required
def delete(expense_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id = %s AND user_id = %s", (expense_id, current_user.id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)