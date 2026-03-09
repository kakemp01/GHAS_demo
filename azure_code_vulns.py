"""
DEMO FILE — INTENTIONALLY INSECURE
Code vulnerabilities for GitHub Advanced Security Code Scanning demo.
No real secret patterns — safe to push past push protection.
"""

import os
import pickle
import subprocess
import hashlib
import sqlite3
import xml.etree.ElementTree as ET
import requests
from flask import Flask, request, redirect, send_file, make_response, jsonify

app = Flask(__name__)

# ──────────────────────────────────────────────
# Fake credentials (not matching provider patterns,
# so push protection won't block them)
# ──────────────────────────────────────────────
DB_HOST = "prod-db.internal.example.com"
DB_USER = "admin"
DB_PASSWORD = "P@ssw0rd123!"
API_KEY = "demo-api-key-not-real-1234567890abcdef"
ADMIN_TOKEN = "my-hardcoded-admin-token-12345"


# ──────────────────────────────────────────────
# ❌ CODE SCANNING TARGETS (CodeQL)
# ──────────────────────────────────────────────


# ── SQL Injection ────────────────────────────

@app.route("/customer")
def get_customer():
    """❌ SQL Injection — user input concatenated into query."""
    customer_id = request.args.get("id")
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    query = "SELECT * FROM customers WHERE id = '" + customer_id + "'"
    cursor.execute(query)
    return jsonify(cursor.fetchall())


@app.route("/users")
def search_users():
    """❌ SQL Injection — f-string in query."""
    name = request.args.get("name")
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE name LIKE '%{name}%'")
    return jsonify(cursor.fetchall())


# ── Command Injection ────────────────────────

@app.route("/ping")
def ping_host():
    """❌ Command Injection — user input in os.system."""
    host = request.args.get("host")
    os.system("ping -c 4 " + host)
    return {"status": "done"}


@app.route("/diagnostics")
def run_diagnostics():
    """❌ Command Injection — user input in subprocess with shell=True."""
    cmd = request.args.get("cmd")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return {"output": result.stdout}


# ── Unsafe Deserialization ───────────────────

@app.route("/process", methods=["POST"])
def process_message():
    """❌ Unsafe Deserialization — pickle.loads on untrusted data."""
    data = request.get_data()
    obj = pickle.loads(data)
    return {"result": str(obj)}


# ── Path Traversal ───────────────────────────

@app.route("/download")
def download_file():
    """❌ Path Traversal — user-controlled filename in file access."""
    filename = request.args.get("file")
    return send_file("/var/data/" + filename)


@app.route("/read")
def read_file():
    """❌ Path Traversal — open() with user-controlled path."""
    filepath = request.args.get("path")
    with open(filepath, "r") as f:
        content = f.read()
    return {"content": content}


# ── Server-Side Request Forgery (SSRF) ──────

@app.route("/fetch")
def fetch_url():
    """❌ SSRF — user-controlled URL passed to requests.get."""
    url = request.args.get("url")
    resp = requests.get(url)
    return resp.content


# ── Open Redirect ────────────────────────────

@app.route("/redirect")
def open_redirect():
    """❌ Open Redirect — unvalidated redirect destination."""
    target = request.args.get("next")
    return redirect(target)


# ── Cross-Site Scripting (XSS) ──────────────

@app.route("/search")
def search():
    """❌ Reflected XSS — user input rendered in HTML without escaping."""
    query = request.args.get("q", "")
    html = "<h1>Results for: " + query + "</h1>"
    return make_response(html)


@app.route("/welcome")
def welcome():
    """❌ Reflected XSS — user input in HTML response."""
    username = request.args.get("name", "")
    return f"<html><body><p>Welcome, {username}!</p></body></html>"


# ── Code Injection ───────────────────────────

@app.route("/calc", methods=["POST"])
def calc():
    """❌ Code Injection — eval() on user-supplied expression."""
    expr = request.json.get("expr")
    result = eval(expr)
    return {"result": str(result)}


@app.route("/run", methods=["POST"])
def run_code():
    """❌ Code Injection — exec() on user-supplied code."""
    code = request.json.get("code")
    exec(code)
    return {"status": "executed"}


# ── Weak Cryptographic Hashing ───────────────

@app.route("/login", methods=["POST"])
def login():
    """❌ Weak Hashing — MD5 for password hashing."""
    password = request.form.get("password")
    password_hash = hashlib.md5(password.encode()).hexdigest()
    return {"hash": password_hash}


@app.route("/verify", methods=["POST"])
def verify():
    """❌ Weak Hashing — SHA1 for password hashing."""
    password = request.form.get("password")
    password_hash = hashlib.sha1(password.encode()).hexdigest()
    return {"hash": password_hash}


# ── Hardcoded Credentials ────────────────────

@app.route("/admin")
def admin_panel():
    """❌ Hardcoded credential in authentication check."""
    token = request.headers.get("Authorization")
    if token == "Bearer " + ADMIN_TOKEN:
        return {"status": "admin access granted"}
    return {"status": "forbidden"}, 403


@app.route("/db")
def db_connect():
    """❌ Hardcoded password in connection string."""
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    return {"status": "connected", "user": DB_USER, "password": DB_PASSWORD}


# ── Log Injection ────────────────────────────

@app.route("/log")
def log_activity():
    """❌ Log Injection — unsanitized user input written to logs."""
    user = request.args.get("user")
    app.logger.info("User logged in: " + user)
    return {"status": "logged"}


# ── XML External Entity (XXE) ────────────────

@app.route("/parse-xml", methods=["POST"])
def parse_xml():
    """❌ XXE — parsing untrusted XML without disabling external entities."""
    xml_data = request.get_data()
    root = ET.fromstring(xml_data)
    return {"tag": root.tag, "text": root.text}


# ── Insecure Temporary File ──────────────────

@app.route("/export")
def export_data():
    """❌ Insecure temp file — predictable path, world-readable."""
    data = request.args.get("data", "")
    tmp_path = "/tmp/export_data.txt"
    with open(tmp_path, "w") as f:
        f.write(data)
    return send_file(tmp_path)


# ── Missing CSRF / Sensitive GET ─────────────

@app.route("/delete-account")
def delete_account():
    """❌ State-changing action via GET request (no CSRF protection)."""
    user_id = request.args.get("id")
    conn = sqlite3.connect("app.db")
    conn.execute("DELETE FROM users WHERE id = " + user_id)
    conn.commit()
    return {"status": "deleted"}
