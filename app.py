from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for
from sqlalchemy import select
from store.db import db
from store.models import Product, Customer, Category, Order, OrderItem

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
def customers():
    stmt = select(Customer)
    customers = db.session.scalars(stmt).all()
    return render_template("customers.html", customers=customers)


@app.route("/products")
def products():
    stmt = select(Product)
    products = db.session.scalars(stmt).all()
    return render_template("index.html", products=products)


@app.route("/orders")
def orders():
    stmt = select(Order).order_by(Order.order_date.desc())
    orders = db.session.scalars(stmt).all()
    return render_template("orders.html", orders=orders)


@app.route("/orders/<int:id>")
def order_detail(id):
    order = db.session.get(Order, id)

    if not order:
        return render_template("error.html", message="Order not found"), 404
    return render_template("order_detail.html", order=order)


@app.route("/orders/<int:id>/complete", methods=["POST"])
def complete_order(id):
    order = db.session.get(Order, id)

    if not order:
        return render_template("error.html", message="Order not found"), 404

    try:
        order.complete()
        db.session.add(order)
        db.session.commit()
        return redirect(url_for("order_detail", id=id))
    except ValueError as e:
        return render_template("error.html", message=str(e)), 409


@app.route("/categories")
def categories():
    stmt = select(Category).order_by(Category.name)
    categories = db.session.scalars(stmt).all()
    return render_template("categories.html", categories=categories)


@app.route("/categories/<string:name>")
def category_detail(name):
    stmt = select(Category).where(Category.name == name)
    category = db.session.scalar(stmt)

    return render_template(
        "index.html", products=category.products, title=category.name
    )


@app.route("/customers/<int:id>")
def customer_detail(id):
    customer = db.session.get(Customer, id)

    return render_template("customer_detail.html", customer=customer)


@app.route("/cart")
def cart():
    cart_data = session.get("cart", {})

    cart_items = []
    grand_total = 0.0

    for product_id_str, quantity in cart_data.items():
        product_id = int(product_id_str)
        product = db.session.get(Product, product_id)

        if product:
            subtotal = product.price * quantity
            grand_total += subtotal

            cart_items.append(
                {"product": product, "quantity": quantity, "subtotal": subtotal}
            )
    return render_template("cart.html", cart_items=cart_items, grand_total=grand_total)


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    product_id = request.form.get("product_id")
    if "cart" not in session:
        session["cart"] = {}

    cart = session["cart"]
    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    session.modified = True
    # return redirect(url_for("home"))
    target_url = request.referrer or url_for("home")
    return redirect(f"{target_url}#product-{product_id}")


@app.route("/checkout", methods=["POST"])
def checkout():
    cart = session.get("cart", {})

    if not cart:
        return redirect(url_for("products"))

    customer = db.session.get(Customer, 1)
    if not customer:
        return render_template("error.html", message="No default customer found."), 500

    new_order = Order(customer_id=customer.id)
    db.session.add(new_order)

    for product_id_str, quantity in cart.items():
        product_id = int(product_id_str)
        product = db.session.get(Product, product_id)

        if product:
            item = OrderItem(order=new_order, product=product, quantity=quantity)
            db.session.add(item)

    db.session.flush()

    try:
        new_order.complete()
        db.session.commit()
        session.pop("cart", None)
        return redirect(url_for("order_detail", id=new_order.id))
    except ValueError as e:
        db.session.rollback()
        return render_template("error.html", message=f"Checkout failed: {e}"), 409


if __name__ == "__main__":
    app.run(debug=True)
