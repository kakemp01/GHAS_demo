# GitHub Advanced Security – Azure DevSecOps Demo

This repository is used to demonstrate **GitHub Advanced Security (GHAS)** in the context of **Microsoft Azure workloads**.

⚠️ **Important**
This repo intentionally contains **insecure code and fake credentials** for **demo purposes only**.
Do **not** reuse these patterns in production.

---

## Demo Goal

Demonstrate how GitHub Advanced Security protects Azure-based applications by:

- Preventing Azure secrets from being committed
- Detecting application vulnerabilities before deployment
- Securing the software supply chain
- Providing security visibility for developers and security teams

---

## Target Architecture (Demo Context)

The demo code represents a typical Azure workload:

- Python service running on:
  - Azure App Service
  - Azure Functions
  - Azure Container Apps
- Accessing:
  - Azure SQL
  - Azure Storage
  - Azure messaging services (Queue / Service Bus / Event Grid)

The code is **intentionally implemented incorrectly** to show how GHAS detects issues early.

---

## Prerequisites

### Platform Prerequisites

- GitHub Enterprise Cloud or GitHub Enterprise Server
- GitHub Advanced Security enabled for:
  - ✅ Code Scanning
  - ✅ Secret Scanning
  - ✅ Secret Scanning Push Protection
  - ✅ Dependabot Alerts
  - ✅ Dependency Graph
- Permissions to:
  - View Security alerts
  - Create branches and pull requests

### Repository Prerequisites

- Private repository
- Python-based project
- CodeQL workflow enabled for Python

---

## Demo Files

### `azure_insecure_service.py`

This file intentionally contains:

- ❌ Fake Azure credentials (Secret Scanning)
- ❌ SQL Injection (Azure SQL)
- ❌ Command Injection (Azure App Service / Functions)
- ❌ Unsafe Deserialization (Azure messaging)

---

## Demo Setup (Once)

### 1. Create Demo Branch

```bash
git checkout -b demo/azure-ghas-insecure