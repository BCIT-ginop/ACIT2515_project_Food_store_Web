# Project 03: Web development in Python with Flask (part 2)


Make sure you completed and fully understood part 1 of the lab.

At this stage, you must:
* know how SQLAlchemy `ForeignKey` and `relationship` work
* understand and know how to use Flask routes
* understand and know how to use Flask templates and logic
* have a good understanding of URL parameters
* have a good understanding of template scaffolding
* have a clean, functional Flask platform (see part 1):
  * has consistent navigation
  * has a homepage
  * has pages to show products (all, or in a given category)
  * has pages to show categories
  * has pages to show customers and their profiles

## Class diagram

@startuml

class Category {
  + id: int | AUTOINCREMENT
  + name: str
  + products: Product[] | relationship
}

class Product {
  + id: int | AUTOINCREMENT
  + name: str
  + price: float
  + inventory: int
  + category_id: int | ForeignKey
  + categories: Category | relationship
}

class Customer {
  + id: int | AUTOINCREMENT
  + name: str
  + phone: str
  + orders: Order[] | relationship
}

class Order {
  + id: int | AUTOINCREMENT
  + products: ProductOrder[]
  + customer_id: int | ForeignKey
  + customer: Customer | relationship
  + amount: Decimal
  + created: datetime | default: now
  + completed: datetime
  + estimate(): float
  + complete(): bool
}

class ProductOrder {
  + product_id: int | ForeignKey
  + product: Product | relationship
  + order_id: int | ForeignKey
  + order: Order | relationship
  + quantity: int
}

Product -d- Category
Product -r- ProductOrder
ProductOrder -r- Order
Order -d- Customer

@enduml

<div style="page-break-after: always;"></div>

## The `Order` and `ProductOrder` models

You are now going to implement two new classes that will allow you to modelize "orders" made by the customers.

These classes will implement a "many-to-many" relationship: `an order has many products` and `a product can be in many orders`. We can not represent this relationship using a single table - we need to add an "association table" (which is going to be an association object in Python).

For example: `order ID 1` has `10 apples` (product ID 21) and `5 oranges` (product ID 22). You will implement this in the database with:
* an `Order` object (ID 1)
* a `ProductOrder` object for the apples (product_id = 21, quantity = 10, order_id = 1)
* a `ProductOrder` object for the oranges (product_id = 22, quantity = 5, order_id = 1)

### The `Order` model

The model has a foreign key to `Customer`. It also has the following attributes:
* `created`: a `datetime` object which is set when the order is received by the store (= created)
* `completed`: a `datetime` object which is set when the order is completed. The order is complete when:
  * the products have been taken out of the inventory
  * the customer paid for the order
  * when the order is not completed, `completed` is `None` (or `NULL` in SQL).
* `amount`: the total amount for the order. This value is only set when the order is complete (= it can  be NULL or None).

> Why do we have a stage where orders are not complete? You could for instance make an order for 100 apples, but the store only has 50. You don't want to charge the customer for 100 apples if you only have 50 to sell: either the store needs to restock, or the order needs to be adjusted.

### Using `datetime` with SQLAlchemy

`created` and `completed` are now `DATETIME` columns in SQL, so you will need to provide `datetime` objects in Python. For example: `order = Order(customer=tim, created=datetime.now())`. Another option is to set the **default** value of the field. Be careful - do not use `datetime.now()` as the default value in your model, otherwise all your objects will have the same timestamp (i.e., the time at which the model was "loaded").

You can either:
* set the default to `datetime.now` (notice the lack of parentheses)
* import SQL functions from SQLAlchemy (accessible from the `db` object) and use them for the default value: `db.func.now()` is the `NOW()` function in SQL.

```python
class Order(db.Model):
    [...]
    created = db.mapped_column(db.DateTime, nullable=False, default=db.func.now())
    completed = db.mapped_column(db.DateTime, nullable=True, default=None)
    amount = db.mapped_column(db.DECIMAL(6, 2), nullable=True, default=None)
```

### The `ProductOrder` model

Your `ProductOrder` has **TWO** foreign keys: one to the product, and one to the order.

```python
class Order(db.Model):
    # ... other fields
    # add a many-through-many relationship using an intermediary model
    items = db.relationship('ProductOrder', back_populates='order')

class ProductOrder(db.Model):
    # Product foreign key
    product_id = db.mapped_column(db.ForeignKey("product.id"), primary_key=True)
    # Order foreign key
    order_id = db.mapped_column(db.ForeignKey("order.id"), primary_key=True)
    # This is how many items we want in this order
    quantity = db.mapped_column(db.Integer, nullable=False)

    # Relationships and backreferences for SQL Alchemy
    product = db.relationship('Product')
    order = db.relationship('Order', back_populates='items')
```

To represent the order above, you can do the following:

```python
# Create the order
my_order = Order(customer=my_customer)

# Find products
apple_prod = db.session.execute(db.select(Product).where(Product.name == "apple")).scalar()
orange_prod = db.session.execute(db.select(Product).where(Product.name == "orange")).scalar()

# Create individual objects for each "line" of the order
apples = ProductOrder(product=apple_prod, quantity=10, order=my_order)
oranges = ProductOrder(product=orange_prod, quantity=5, order=my_order)
```

## Generate random orders

Create a new function in your `manage.py` file to randomly create several orders. Use the following logic:

* select a random customer from the database
* create a new `Order` for that customer
* select a random number of products from the database
* create a new `ProductOrder` to link each of the products with the order you created before. Use a random "quantity"
* repeat this process as many times as you want (at least 5)

### Use SQL functions for random results

The easiest way to get random records is to use `ORDER BY` and `RAND()` in the select statement. The SQL `RAND()` function is available through `db.func.random()`. For example:

```python
# Gets a random customer from the database
random_customer = db.session.execute(select(Customer).order_by(func.random())).scalar()

# Gets a random number of products (between 4 and 6) from the database
num_prods = random.randint(4, 6)
random_prods = db.session.execute(select(Product).order_by(func.random()).limit(num_prods)).scalars()
```

### Use `random`, `datetime` and `timedelta` to generate random dates

If you use the default value for `created`, it is likely that all your orders will have almost the same creation time. You should also randomize this value. An easy way to do so is to use the `timedelta` library from `datetime`. It allows you to make time computations to generate random dates.

For example:

```python
from random import randint
from datetime import datetime as dt
from datetime import timedelta

dt.now() - timedelta(days=randint(1, 3), hours=randint(0, 15), minutes=randint(0, 30))
```

* `dt.now()`: current date and time
* the date generated will be randomly generated in the past:
  * most recent = 1 day ago
  * oldest = 3 days, 15 hours and 30 minutes ago

## Create HTML views for the orders

Create the following views in your `app.py`:
* `/orders`: shows a list of all orders, including:
  * a link to the order detail page (`/orders/<int:order_id>`)
  * the name of the customer who made the order
  * the date / time at which the order was created
* `/orders/<ORDER_ID>`: shows the order with ID `ORDER_ID`
  * shows the list of products in the order, with their price and quantity
  * shows an estimated amount for the order *if the order was to complete successfully*
* You should pass full `Order` objects to your templates!

Make sure you use templates and template scaffolding! Do not implement any complex logic in the templates.

### Leverage relationships

* If `o` is an `Order` object, then `o.items` is a list of `ProductOrder` objects.
* If `po` is a `ProductOrder` object, then `po.product` is a `Product` object.
* If `p` is a `Product` object, then `p.inventory` is the stock available in store for that product.
* Then, `o.items[0].product.inventory` is the stock available in store for the first product in the order.

For example (adjust for your templates):

```python
for po in o.items:
  print(
    "Name", po.product.name,
    "Price", po.product.price,
    "Quantity", po.quantity,
    "In stock", po.product.inventory
  )
```

### Leverage Object-Oriented Programing

You should not make calculations in the templates (for example, estimated total). This breaks the best practice of keeping business logic (= code) separated from presentation (= HTML templates). Your `Order` class is used to store data in the database, but it is still a regular Python class. You can create a *method* on it to compute the estimated total of the order:

```python
class Order:
  [...]

  def estimate(self):
    total = 0
    for po in self.items:
      one = po.product.price * po.quantity
      total = total + one
    return total
```

Use this function in your templates: `<p>Estimated total: {{ order.estimate() }}</p>`.

## Create a HTML form and a view to `complete` orders

We are now going to let website users "complete" an order. We will need three things:
* a Flask view / URL that triggers order completion
* a way to access the Flask view from the order page
* code / logic to process the order

Because completing the order will incur changes on the database, we cannot use a typical `GET` HTTP method: it would be a bad practice, since `GET` is to *retrieve* data, and we want to *change* data. It is very typical to use a `POST` request in that case.

### Create an HTML form

The only way you can make a `POST` request from a basic HTML page is by submitting a form. In your individual order page template, add a form. Make sure the form method is set to `POST`. Set its "action" to the URL of the Flask view that will process the order. You probably don't have it yet - so make sure the names you are using are consistent.

```html
<form method="post" action="{{ url_for('complete_order', id=order.id) }}">
    <button type="submit">Complete order</button>
</form>
```

The form above, when submitted, will make a POST request to the URL for the `complete_order` function.

### Create the Flask view to handle the order

If using the code above, you will have to create a Flask function called `complete_order` that takes a parameter `id` (integer).

```python
@app.route("/orders/<int:id>/complete", methods=["POST"])
def complete_order(id):
  # COMPLETE THE CODE
```

In this function:
* find the order with ID `id`
* if there is no matching order, return an error message with HTTP code `404` (see below)
* run the order logic
  * if an error occurs, return an error message with HTTP code `400`
  * otherwise, redirect the user to the individual order page. You can also use `url_for` on the Python side. For example: `return redirect(url_for("order", id=id))`.

### Completing an order: logic

To complete an order:
* loop through all `ProductOrder` (.items)
  * for each item, check if the quantity ordered can be fulfilled by the store (inventory)
  * if yes, subtract the quantity ordered from the store inventory
  * if not, interrupt the process and return to the caller without making any changes
    * the easiest is probably to raise an exception, and to catch it in the Flask view!
* set the `completed` attribute to the date/time of "now". You may use `db.func.now()` from SQLAlchemy!
* set the `amount` attribute to the total amount of the order
* commit the changes to the database

> You should implement that logic in the model, for instance with a `def complete(self)` method on the `Order` class.

If you raise a `ValueError` exception in the method above, then your Flask view could look like:

```python
# order is the Order object
try:
    order.complete()
    db.session.add(order)
    db.session.commit()
except ValueError as e:
    return render_template("error.html", message=f"{e}"), 409
```

### Creating a custom error page - HTTP status codes

It is useful to have a customized error page that tells the user what happened and why. This is done in the view above (`error.html`). You can then use this page whenever an "error" occurs.

You should use it with the relevant HTTP status codes for errors. In the example above, the page returned has a status code `409` (resource conflict), but you may also use it for your `404` pages (resource not found). Make sure you are familiar with HTTP status codes!

### Adjust the order page

Make changes to the order page to:
* make it look different when an order is complete or not
* highlight which items in the order are likely to cause an error (not enough of them)

## Connect the customer and order pages

* On your individual order page, make sure there is a link to the customer page (= customer who made the order).
* On the customer page, add a new HTML section with a list of all orders made by that user, with a link to each relevant order page.
* You should be able to navigate between the order pages and the customer pages just using links.
* Split the HTML section in two: put pending orders on top, and completed orders below.

> :bulb: The easiest way to do that is to create a method on the `Customer` class!

* a method on `Customer` has access to `self` (= the customer object)
* there should be a relationship from `Customer` to `Order`...
* ... so `self.orders` (adjust to your models) contains a list of all orders
* an order is pending when its attribute `completed` is `None` (or `NULL` in SQL)
* an order is complete when its attribute `completed` is not `None`

Write the methods - they are good candidates for list comprehensions.

> :warning: You should not have to make any additional queries.

<div style="page-break-after: always;"></div>

## Project Stage completion

Use the following list to make sure this stage of the project is complete.

### Python code

1. `db.py` - database engine and connectivity
2. `models.py` - class definitions
   1. with added methods on the `Order` class (estimated total and order completion)
3. `app.py` - Flask views
4. `manage.py` - management script (to import data and generate random orders)
5. Understanding of Flask routes and decorators, SQLAlchemy interaction, exception handling

### Flask views and URLs

1. `/` - homepage
2. `/products` - list of products
3. `/categories` - list of categories, with link to category pages
4. `/categories/<CATEGORY_NAME>` - individual category page
5. `/customers` - list of customer, with link to customer pages
6. `/customers/<CUSTOMER_ID>` - individual customer page, with order list
7. `/orders` - list of orders
8. `/orders/<ORDER_ID>` - individual order page, with "Complete" button / form

### Flask templates

1. templates are using scaffolding with `{% block %}` and `{% extends %}`
2. templates are using `url_for` for links and static assets
3. there is a template for error pages that allows custom messages to be displayed