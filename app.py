from flask import Flask, render_template
from sqlalchemy import select
from store.database import Session
from store.models import Product, Category

app = Flask(__name__)


@app.route("/")
def home():
    with Session() as session:
        stmt = select(Product)
        products = session.scalars(stmt).all()

        html_output = "<h1>Welcome to the Food Store</h1>"
        html_output = "<ul>"

        for product in products:
            stock_msg = f"(Stock: {product.available})"
            if product.available == 0:
                stock_msg = "<strong>(OUT OF STOCK)</strong>"

            html_output += f"<li>{product.name} - ${product.price} {stock_msg}</li>"

        html_output += "<ul>"
        return html_output


if __name__ == "__main__":
    app.run(debug=True)
