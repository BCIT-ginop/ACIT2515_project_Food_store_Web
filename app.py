from pathlib import Path
from flask import Flask, render_template
from sqlalchemy import select
from store.db import db
from store.models import Product, Customer

app = Flask(__name__)

app.instance_path = Path(".").resolve()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///store.db"

db.init_app(app)


@app.route("/")
def home():
    stmt = select(Product)
    products = db.session.scalars(stmt).all()
    return render_template("index.html", products=products)


@app.route("/customers")
def customer():
    stmt = select(Customer)
    customers = db.session.scalars(stmt).all()
    return render_template("customers.html", customers=customers)


if __name__ == "__main__":
    app.run(debug=True)
