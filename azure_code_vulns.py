"""
DEMO FILE — INTENTIONALLY INSECURE
Code vulnerabilities for GitHub Advanced Security Code Scanning demo.
"""

import os
import pickle
import subprocess
import hashlib
import sqlite3
import yaml
import requests
from flask import Flask, request, redirect, send_file, make_response, jsonify

app = Flask(__name__)


# ──────────────────────────────────────────────
# ❌ SECRETS — for Secret Scanning demo
# ──────────────────────────────────────────────

# ❌ Slack Bot Token
SLACK_TOKEN = "xoxb-123456789012-1234567890123-ABCDEFabcdef123456abcdef"

# ❌ SendGrid API Key
SENDGRID_KEY = "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"

# ❌ Stripe API Key
STRIPE_KEY = "sk_live_51HG3CMJ8xTR2D4F5g6H7j8K9L0mNpQrStUvWxYz"


# ──────────────────────────────────────────────
# ❌ CODE SCANNING VULNERABILITIES (CodeQL)
# ──────────────────────────────────────────────


# ── 1. SQL Injection (CWE-89) ────────────────

@app.route("/customer")
def get_customer():
    customer_id = request.args.get("id")
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE id = '" + customer_id + "'")
    rows = cursor.fetchall()
    return jsonify(rows)


@app.route("/users")
def search_users():
    name = request.args.get("name")
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE name LIKE '%{name}%'")
    rows = cursor.fetchall()
    return jsonify(rows)


# ── 2. Command Injection (CWE-78) ────────────

@app.route("/ping")
def ping_host():
    host = request.args.get("host")
    os.system("ping -c 4 " + host)
    return "done"


@app.route("/diagnostics")
def run_diagnostics():
    cmd = request.args.get("cmd")
    output = subprocess.check_output(cmd, shell=True)
    return output


# ── 3. Code Injection (CWE-94) ───────────────

@app.route("/calc", methods=["POST"])
def calc():
    expr = request.form.get("expr")
    result = eval(expr)
    return str(result)


@app.route("/run", methods=["POST"])
def run_code():
    code = request.form.get("code")
    exec(code)
    return "executed"


# ── 4. Unsafe Deserialization (CWE-502) ──────

@app.route("/process", methods=["POST"])
def process_message():
    data = request.get_data()
    obj = pickle.loads(data)
    return str(obj)


@app.route("/load-yaml", methods=["POST"])
def load_yaml_data():
    raw = request.get_data()
    obj = yaml.load(raw, Loader=yaml.Loader)
    return str(obj)


# ── 5. Path Traversal (CWE-22) ───────────────

@app.route("/download")
def download_file():
    filename = request.args.get("file")
    path = "/var/data/" + filename
    return send_file(path)


@app.route("/read")
def read_file_endpoint():
    filepath = request.args.get("path")
    f = open(filepath, "r")
    content = f.read()
    f.close()
    return content


# ── 6. SSRF (CWE-918) ────────────────────────

@app.route("/fetch")
def fetch_url():
    url = request.args.get("url")
    resp = requests.get(url)
    return resp.text


# ── 7. Open Redirect (CWE-601) ───────────────

@app.route("/redirect")
def open_redirect():
    target = request.args.get("next")
    return redirect(target)


# ── 8. Reflected XSS (CWE-79) ────────────────

@app.route("/search")
def search():
    query = request.args.get("q", "")
    return make_response("<h1>Results for: " + query + "</h1>")


@app.route("/greet")
def greet():
    name = request.args.get("name", "")
    return "<html><body>Hello " + name + "</body></html>"


# ── 9. Weak Hashing (CWE-327/328) ────────────

@app.route("/login", methods=["POST"])
def login():
    password = request.form.get("password")
    hashed = hashlib.md5(password.encode()).hexdigest()
    return jsonify({"hash": hashed})


# ── 10. Log Injection (CWE-117) ──────────────

@app.route("/log")
def log_activity():
    user = request.args.get("user")
    app.logger.info("Login: " + user)
    return "logged"


# ── 11. SQL Injection via DELETE (CWE-89) ────

@app.route("/delete-account")
def delete_account():
    user_id = request.args.get("id")
    conn = sqlite3.connect("app.db")
    conn.execute("DELETE FROM users WHERE id = " + user_id)
    conn.commit()
    return "deleted"
