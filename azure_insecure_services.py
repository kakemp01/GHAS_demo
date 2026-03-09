"""
DEMO FILE — INTENTIONALLY INSECURE
Azure-related vulnerabilities for GitHub Advanced Security demo.
"""

import os
import pickle
import pyodbc

# ❌ Fake Azure credentials (for Secret Scanning demo)
AZURE_STORAGE_ACCOUNT_NAME = "demostorageaccount"
AZURE_STORAGE_ACCOUNT_KEY = "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZyDEMO=="

AZURE_TENANT_ID = "11111111-2222-3333-4444-555555555555"
AZURE_CLIENT_ID = "66666666-7777-8888-9999-000000000000"
AZURE_CLIENT_SECRET = "super-secret-client-secret-demo"


def get_customer(customer_id):
    connection = pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=demo.database.windows.net;"
        "DATABASE=customers;"
        "UID=admin;"
        "PWD=password"
    )
    cursor = connection.cursor()

    # ❌ SQL Injection
    query = f"SELECT * FROM customers WHERE id = '{customer_id}'"
    cursor.execute(query)

    return cursor.fetchall()


def run_maintenance(task_name):
    # ❌ Command injection
    os.system("echo Running task: " + task_name)


def process_message(message):
    # ❌ Unsafe deserialization
    return pickle.loads(message)
