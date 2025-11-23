# Project 02: Web development in Python with Flask (part 1)


In this part of the project, we are going to build a web application that displays information
using HTML. We are going to use the `flask` library. You must install it with
pip first: `uv add flask`.

## Understand Flask

Flask is a web micro-framework that allows Python developers to very quickly
create web applications and APIs with minimal code involved.

### Basic structure of a Flask application

The minimal version of a Flask application is:

```python
from flask import Flask

app = Flask(__name__)

if __name__ == "__main__":
    app.run(debug=True, port=8888)
```

This will run a Flask web application, in debug mode, listening on port 8888.
Run it with: `python app.py`.

> :warning: By default, the application listens only on the local interfaces, so
> it is not available to anyone else but you. This also means that you must
> access it using `localhost` or `127.0.0.1`.

> :bulb: Running the app in debug mode sets up live reload: the app will reload
> itself whenever you make changes to the code. Make sure you reload the web
> pages in your browser, though...

> :warning: follow the steps in the project, unless **you already know what you are
> doing**. For example, the application can be run with `flask run`. However, in
> order for it to work well and consistently, you would need a full
> understanding of Flask, your terminal settings, your Python installation, and
> your system configuration

### Understanding routes and URLs

The `app` variable is a Flask instance and can be used to interact with Web
methods and HTTP requests. You can use it to create "routes" in your application
that link web requests to python functions and classes and return data to the
web browser. A Flask route is just a Python function, that returns at least one
value, typically a string (= the HTML code to be displayed in the browser).

```python
@app.route("/")
def home():
    return "<h1>HEY THERE</h1>"
```

The function above will be called whenever an HTTP request is made on the route
`/` (which is the default URL when accessing the website with a browser). If you
browse to `http://127.0.0.1:8888/` you should see the text above displayed in
the browser. Try to change it and refresh the browser page. Try to add more HTML
code to the string returned.

### Using templates

It is very inconvenient to return raw HTML directly from the Python code, and it
breaks best practices (separation of code and presentation). It is much better
to use _templates_, aka HTML documents whose structure is fully created and
complete. We can then just "fill" them with the information we want.

Flask looks for templates in the `templates` folder by default. Create it and
put your HTML templates in this folder. You can then render a template by
calling the `render_template` function from Flask, and then return the value to
the browser. Make sure you import it first!

```python
from flask import Flask, render_template

@app.route("/")
def home():
    return render_template("home.html")
```

You can specify where "placeholders" should be in your template, and provide
values for the placeholders in the `render_template` function.

```html
<h3>My name is {{ name }}</h3>
```

With the HTML template above, `render_template` will replace `{{ name }}` with
the value provided as the keyword argument `name=`. For example:
`render_template("home.html", name="Tim")`.

`{{ ... }}` will update the template with the result of the Python expression
provided. It is usually a variable.

You can also run logic by using `{% ... %}`. For example, the following will
loop on the list `my_list`:

```html
<ul>
    {% for element in my_list %}
        <li>List element: {{ element }}</p>
    {% endfor %}
</ul>
```

Try it: `render_template("home.html", my_list=["Tim", "Bob", "Alice"])`.

## Write your first view

Create a new route in your Flask application for the route `/` (this is the
default route when you don't provide a specific URL).

This route just displays the "homepage" of your web shop. Create a template,
fill it with the HTML of your choice, and use it in the view.

### Adding images

If you want to use local files (for example: images; CSS, or Javascript files):

- create a folder `static` in your Flask directory
- put your static files in this folder
- use `url_for` against the `static` route to resolve the URL to your files:
  - `url_for("static", filename="style.css")`
  - `{{ url_for("static", filename="logo.jpg") }}`

## Configure Flask to use a database with SQLAlchemy

We can configure Flask to use a SQLAlchemy database. The module
`flask-sqlalchemy` does a lot of the heavy lifting (database connection,
declarative base, session management).

Install it with `uv add flask-sqlalchemy`.

### Flask setup

In your `app.py`, add the following lines:

```python
app = Flask(__name__)
# This will make Flask use a 'sqlite' database with the filename provided
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///i_copy_pasted_this.db"
# This will make Flask store the database file in the path provided
app.instance_path = Path("change_this").resolve()
# Adjust to your needs / liking. Most likely, you want to use "." for your instance path. This is up to you. You may also use "data".
```

- `.config[SQLALCHEMY_DATABASE_URI]` will be used to create an engine.
- `.instance_path` is a path to the folder where the database file (among
  others) will be looked up. The path is relative to the root of your Flask
  folder.

### Database setup

Setup Flask-SQLAlchemy to use the ORM. Create a file `db.py` and use the
following code:

```python
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
```

> :bulb: This creates an object `db` which we can use for all tasks requiring
> the database: defining models, querying from and saving to the database. This
> object has the `Base` class registered as the base class for ORM-related
> features. We could make changes to this base class, but it is not required for
> the project yet 

You can use: `db.mapped_column`, `db.relationship`, `db.Integer`,
`db.ForeignKey`, etc.

### Connect the database with Flask

Make sure you connect your `db` object with your Flask `app` object. In
`app.py`:

```python
db.init_app(app)
```

## Create your models

Recreate the classes from the first portion of the Project Project: Food Store 
You can create your classes exactly like you have done with SQLAlchemy alone.
The main differences is that your classes should inherit from `db.Model` instead
of `Base`. Write your models in the `models.py` file.

```python
from db import db

class Product(db.Model):
  [...] # Entity declaration

```

Note that the `__tablename__` attribute is not strictly required: if not
specified, it will be auto-generated. It is a good idea to set it explicitly, as
we use it in relationships / foreign keys.

> :bulb: You should be able to reuse much of your existing SQLAlchemy classes
> from the previous project lab. With the noted changes

## Create a script to setup the database

Before using the database, we must create it, and insert data into it.

- `db.create_all()` will create all tables (and the SQLite database if it does
  not exist)
- `db.drop_all()` will drop all tables

Once the database and tables are created, we can save objects to the database:

- we create instances of our classes
- we can then add them to the 'session'
- the session is automatically provided by the Flask-SQLAlchemy module, using
  the `db.session` variable.

For example:

```python
for category in ("travel", "fun"):
    # Create a new instance
    obj = Category(name=category)
    # Adds it to the session
    db.session.add(obj)
# Commit the session changes to the database (outside of the loop)
db.session.commit()
```

### Start writing the script

Create a separate Python file (for example, `manage.py`). This file will be used
to manage our database.

Reuse your work: `manage.py` will work almost the same as `main.py` from the
previous project lab (but you will use the `db` object rather than plain SQLAlchemy
instructions).

### Setting the application context

Flask-SQLAlchemy allows you to make database requests when the app is running
through `python app.py`. A session is created for every incoming request, and
cleaned up afterwards.

However, `manage.py` is a different Python file that will run independently from
the app. In order to make database requests, you will need to setup an "app
context" first. You can do it in two ways:

- use a `with` block
- `push()` the context

See examples below:

```python
# USING A WITH BLOCK
if __name__ == "__main__":
  with app.app_context():
    drop_tables()
    create_tables()
    obj = Category(name="dairy")
    db.session.add(obj)
    db.session.commit()

  # USING PUSH
  app.app_context().push()
  drop_tables()
  create_tables()
  obj = Category(name="dairy")
  db.session.add(obj)
  db.session.commit()
```

In `manage.py`, create separate functions for each of the following:

- drop all tables from the database
- create all tables in the database
- import data from the "products.csv" and "customers.csv" files

You should be able to reuse most of the code from previous labs!

> :bulb: You will need to import `db` from `db.py` and `app` from `app.py` !

Then, call the functions as required in the `if __name__ == "__main__"` block of
your script. Make sure your functions are called with a "context" set.

Run the script and check that your database now contains records.

## Create views that use the database objects

We now have records in our database. We can use them to display HTML content.

- You can create `SELECT` SQL statements with `db.select`.
- For example:
  - `statement = db.select(User).order_by(User.name)`
  - `statement = db.select(User).where(User.name == "Tim")`
- You can _execute_ these statements in the current session with
  `records = db.session.execute(statement)`.
- `SELECT` statements return a list of "database records". You must use
  `.scalars()` or `.scalar()` to obtain the actual results.
- `results = records.scalars()` (for a list of records, `.scalar()` for a single
  record)
- The results returned are instances of the `User` class.

Write HTML views for the following routes:

- `/products`: displays all products in the store
- `/categories`: displays all categories
- `/customers`: displays all customers

> :bulb: Remember - if `product` is an object, then you can use
> `{{ product.name }}` in your template to get the `name` attribute of your
> product object.

## Create a route that takes in a URL parameter

There are situations where the URL contains relevant information for the view.
For example, `/categories/dairy` could be a page that lists all the products
that belong to the "Dairy" category.

In Flask, you can use a route parameter like this:

```python
@app.route("/categories/<string:name>")
def category_detail(name):
    stmt1 = db.select(Category).where(Category.name == name)
    # Find the category with name 'name'
    cat = db.session.execute(statement).scalar()
    cat.products # contains all the products in that category (use back_populates)
    # ...
```

Note how `name` is specified in the `route` decorator, and is an argument of
your view function.

There are different ways to obtain the same results. Note the first example is
_replicating_ the work that SQLAlchemy already does with relationships - this is
for comprehension purposes and _should not be used as-is_.

```python
# EXPLICIT SELECT FROM PRODUCTS TABLE
@app.route("/categories/<string:name>")
def category_detail(name):
    stmt1 = db.select(Category).where(Category.name == name)
    # Find the category with name 'name'
    cat = db.session.execute(statement).scalar()
    # Now, find products with a matching 'category_id'
    stmt2 = db.select(Product).where(Book.category_id == cat.id)
    # ...
```

The following queries the relationship using the relationship from `Product` to
`Category`.

```python
# QUERYING THE RELATIONSHIP WITH HAS
stmt = db.select(Product).where(Product.category.has(Category.name == name))
products = db.execute(stmt).scalars()
```

Create the following views:

- `/categories/<string:name>`: shows all products in category with ID `id`
- `/customers/<int:id>`: shows the customer page for customer ID `id` (note:
  there is not much to display on that page yet!)

### URL converters

The following
[URL converters](https://flask.palletsprojects.com/en/2.0.x/api/#url-route-registrations)
are available and commonly used:

- `<string:variable>`: strings without any `/` (default)
- `<int:variable>` and `<float:variable>` for numbers
- `<path:variable>` for strings including `/`

## Connect pages with links: `url_for`

In your HTML template for the page with the list of all categories, add links to
the category _detail_ pages.

It would be tempting to hardcode the links in the template, for example
`/categories/{{ category.id}}`.. However, if the route changes in Flask (in the
`@app` decorator), all the related links will break. Instead, you **SHOULD USE**
`url_for` which returns the URL for a specific view. `url_for` takes the **name
of the function** as first parameter. If the view uses arguments, make sure you
provide them in the keyword format (`parameter=value`). You should use:

```html
<a href="{{ url_for('home') }}">Homepage</a>
<a href="{{ url_for('category_detail', category=category.id) }}"
  >{{ category.name }}</a
>
```

**The parameter to `url_for` is not the URL but the _FLASK FUNCTION NAME_.**

### Keep going: customers

Create a view for `/customers/<int:id>` that displays the page for a given
customer. Add links to the `/customers` page so you can easily see profile pages
for all your customers.

### Use blocks and template scaffolding

It is very inconvenient to write a complete HTML file for every view / function
we have in Flask. It is very likely that many if not all of our pages will have
the same structure, and only specific "areas" (or "blocks") of the page will
change.

This can be done by using _template scaffolding_, where you can build templates
based on other templates.

Take a look at the template `[base.html](./starter/base.html)`. You can see that it contains a basic
HTML document, with a specific instruction: `{% block content %}{% endblock %}`.
This defines a new _block_ that can be overriden by a child template.

Now, take a look at the template `[customers.html](./starter/customers.html)`. You can see that the template
is very short.

1. It _extends_ the base template with `{% extends "base.html" %}`.
2. It overrides the `content` block with its own data.

Make changes to the `base.html` file, and the templates you already wrote to use
template scaffolding.

> :bulb: You may want to add styling to your HTML. Define CSS in the `<head>` of
> your base HTML template, and add classes / IDs as required to the HTML code.
> You may also use an existing HTML/CSS template (for example,
> [Bootstrap](https://getbootstrap.com/docs/5.0/getting-started/introduction/#starter-template)).

You can also use `url_for` to load "static" files (for example, CSS or JS
files):

```html
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}" />
```

## Polish your project

- If you are using CSS, move the CSS code to a separate file in the `static`
  folder.
- Clean up the views to use templates throughout.

<div style="page-break-after: always;"></div>

## Project Stage Completion

This part of the project is complete when:

- you have a Flask platform working, with pages for all products, all
  categories, all customers, as well as individual category and customer pages.
- your Flask application uses the contents from the SQL database.
- you are using Flask templates.
- your templates use links and `url_for` for easy navigation.
- you can easily drop and create the tables, as well as import all the data from
  the CSV files.
