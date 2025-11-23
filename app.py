from pathlib import Path
from flask import Flask, render_template
from sqlalchemy import select
from store.db import db
from store.models import Product, Customer, Category

app = Flask(__name__)

app.secret_key = "secret"

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


@app.route("/products")
def products():
    stmt = select(Product)
    products = db.session.scalars(stmt).all()
    return render_template("index.html", products=products)


@app.route("/categories")
def categories():
    stmt = select(Category).order_by(Category.name)
    categories = db.session.scalars(stmt).all()
    return render_template("categories.html", categories=categories)


@app.route("/categories/<string:name>")
def category_detail(name):
    stmt = select(Category).where(Category.name == name)
    category = db.session.scalar(stmt)

    if category is None:
        return f"Category '{name}' not found", 404

    return render_template(
        "index.html", products=category.products, title=category.name
    )


@app.route("/customers/<int:id>")
def category_detail(id):
    customer = db.session.get(Customer, id)

    if not customer:
        return "Customer not found", 404

    return render_template("customer_detail.html", customer=customer)


if __name__ == "__main__":
    app.run(debug=True)
