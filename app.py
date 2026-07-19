from flask import Flask, render_template, request, redirect, url_for
from datetime import date

app = Flask(__name__)

expenses = []

@app.route("/")
def home():
    total = sum(e["amount"] for e in expenses)
    return render_template("home.html", expenses=expenses, total=total)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        amount = float(request.form["amount"])
        category = request.form["category"]
        description = request.form["description"]
        expenses.append({
            "amount": amount,
            "category": category,
            "description": description,
            "date": str(date.today())
        })
        return redirect(url_for("home"))
    return render_template("add.html")

@app.route("/delete/<int:index>")
def delete(index):
    if 0 <= index < len(expenses):
        expenses.pop(index)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)