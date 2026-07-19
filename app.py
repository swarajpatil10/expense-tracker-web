from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expenses.db"
db = SQLAlchemy(app)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(20), nullable=False)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    expenses = Expense.query.all()
    total = sum(e.amount for e in expenses)
    return render_template("home.html", expenses=expenses, total=total)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        amount = float(request.form["amount"])
        category = request.form["category"]
        description = request.form["description"]
        expense = Expense(amount=amount, category=category,
                         description=description, date=str(date.today()))
        db.session.add(expense)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add.html")

@app.route("/delete/<int:id>")
def delete(id):
    expense = Expense.query.get(id)
    if expense:
        db.session.delete(expense)
        db.session.commit()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)