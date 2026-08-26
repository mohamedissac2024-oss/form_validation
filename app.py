import os
import psycopg2

from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret")


def get_db():
    return psycopg2.connect(os.environ.get("DATABASE_URL"))


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            phone VARCHAR(50),
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


@app.route("/")
def home():
    return render_template("form.html")


@app.route("/submit", methods=["POST"])
def submit():

    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    message = request.form.get("message")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO clients (name, email, phone, message)
        VALUES (%s, %s, %s, %s)
    """, (name, email, phone, message))

    conn.commit()

    cursor.close()
    conn.close()

    return "Information saved successfully!"


# -------------------------
# ADMIN LOGIN
# -------------------------

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "mahat123456"


def admin_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))

        return f(*args, **kwargs)

    return decorated_function


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

            session["admin_logged_in"] = True

            return redirect(url_for("admin_dashboard"))

        return "Invalid username or password"

    return render_template("admin_login.html")


@app.route("/admin")
@admin_required
def admin_dashboard():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, email, phone, message, created_at
        FROM clients
        ORDER BY created_at DESC
    """)

    clients = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin.html", clients=clients)


@app.route("/admin/logout")
def admin_logout():

    session.pop("admin_logged_in", None)

    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)