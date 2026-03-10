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

### GitHub Requirements

| Requirement | Details |
|---|---|
| **GitHub Plan** | GitHub Enterprise Cloud **or** GitHub Enterprise Server 3.x+ |
| **GHAS License** | GitHub Advanced Security must be licensed and enabled for the organization |
| **Repository Visibility** | Private repository (GHAS is free on public repos, but demo assumes private) |
| **Permissions** | Repo admin or org owner to enable security features |

### Features to Enable

Go to **Settings → Code security and analysis** on the repository and enable:

- [x] **Dependency graph**
- [x] **Dependabot alerts**
- [x] **Dependabot security updates** (optional)
- [x] **Code scanning** (via CodeQL)
- [x] **Secret scanning**
- [x] **Secret scanning push protection**

### CodeQL Workflow

A CodeQL Actions workflow must be configured. If not already present, add one via:

1. Go to the **Actions** tab → **New workflow**
2. Search for **"CodeQL Analysis"**
3. Select the starter workflow and commit it
4. Ensure **Python** is listed as an analyzed language

Minimal workflow (`.github/workflows/codeql.yml`):

```yaml
name: "CodeQL"

on:
  push:
    branches: [main, ghas_demo]
  pull_request:
    branches: [main]

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write

    strategy:
      matrix:
        language: [python]

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}

      - name: Autobuild
        uses: github/codeql-action/autobuild@v3

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3
```

### Local Tooling (Optional)

Only needed if you want to demo locally before pushing:

- Python 3.10+
- Git CLI
- GitHub CLI (`gh`) — for creating PRs from the terminal

---

## Repository Structure

| File | Purpose |
|---|---|
| `azure_code_vulns.py` | Flask app with 11+ CodeQL-detectable vulnerabilities and hardcoded secrets |
| `azure_insecure_services.py` | Azure SDK–style code with SQL injection, command injection, unsafe deserialization, and fake Azure credentials |
| `requirements.txt` | Python dependencies (also triggers Dependabot if outdated) |

---

## Demo Approach

### Recommended Flow

Run the demo in this order to build a narrative from **secrets → code vulnerabilities → supply chain**:

#### Part 1 — Secret Scanning (Push Protection)

> *"Let's see what happens when a developer accidentally commits a secret."*

1. Show the hardcoded secrets in `azure_code_vulns.py` (Slack token, SendGrid key, Stripe key)
2. Show the fake Azure credentials in `azure_insecure_services.py`
3. Attempt to push — **Push Protection blocks the push** if the secrets match known patterns
4. Walk through the alert in **Security → Secret scanning**
5. Show options: revoke, dismiss as false positive, or mark as used in tests

#### Part 2 — Code Scanning (CodeQL)

> *"Now let's look at what CodeQL finds in our application code."*

1. Push or open a PR against `main` to trigger the CodeQL workflow
2. Wait for the analysis to complete (~2–5 min)
3. Navigate to **Security → Code scanning alerts**
4. Walk through key findings:
   - SQL Injection (`/customer`, `/users`, `/delete-account`)
   - Command Injection (`/ping`, `/diagnostics`)
   - Code Injection (`/calc` via `eval()`, `/run` via `exec()`)
   - Unsafe Deserialization (`/process` via `pickle.loads`, `/load-yaml`)
   - Path Traversal (`/download`, `/read`)
   - SSRF (`/fetch`)
   - Open Redirect (`/redirect`)
   - Reflected XSS (`/search`, `/greet`)
   - Weak Hashing (`/login` using MD5)
5. Show the data-flow view: source → sink tracing
6. Show how to dismiss or open an issue from an alert

#### Part 3 — Dependabot / Supply Chain

> *"Finally, let's check our dependencies."*

1. Navigate to **Security → Dependabot alerts**
2. Show any alerts on `flask` or `requests` (if vulnerable versions are pinned)
3. Show the dependency graph under **Insights → Dependency graph**
4. Optionally show Dependabot auto-PR for version bumps

---

## How to Force Code Scanning Alerts

CodeQL alerts are generated when the CodeQL workflow runs against code containing known vulnerability patterns. Here's how to trigger them on demand:

### Option A — Push to a Monitored Branch

```bash
# Make any change (or add a new vulnerability)
git add .
git commit -m "Add insecure code for demo"
git push origin ghas_demo
```

The CodeQL workflow runs on push if `ghas_demo` is in the `on.push.branches` list.

### Option B — Open a Pull Request

```bash
git checkout -b demo/insecure-code
# Edit or add vulnerable code
git add .
git commit -m "Demo: add vulnerable endpoint"
git push origin demo/insecure-code
```

Then open a PR targeting `main`. CodeQL runs automatically and alerts appear as **PR check annotations** inline in the diff.

### Option C — Add a New Vulnerability to Force a Fresh Alert

Append a new vulnerable endpoint to `azure_code_vulns.py`:

```python
# ── NEW: SQL Injection via search ─────────────
@app.route("/orders")
def get_orders():
    status = request.args.get("status")
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE status = '" + status + "'")
    return jsonify(cursor.fetchall())
```

Commit and push — a **new** code scanning alert will appear after the workflow completes.

### Option D — Manual Workflow Trigger

Add `workflow_dispatch` to the CodeQL workflow to allow manual runs:

```yaml
on:
  workflow_dispatch:
  push:
    branches: [main, ghas_demo]
```

Then trigger from **Actions → CodeQL → Run workflow**.

### Verifying Alerts

- Go to **Security → Code scanning alerts**
- Filter by severity, rule, or file
- Each alert shows the exact line, data flow, and CWE reference

---

## How to Force Secret Scanning Alerts

Secret scanning detects credentials that match known provider patterns. Here's how to trigger and demonstrate it:

### Option A — Push an Existing Secret (Push Protection Demo)

1. Ensure **push protection** is enabled (Settings → Code security → Secret scanning → Push protection)
2. Add or uncomment a real-format secret in any file, e.g.:

```python
# GitHub Personal Access Token (classic format)
GITHUB_PAT = "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdef12"
```

3. Commit and push:

```bash
git add .
git commit -m "Add token"
git push
```

4. **Push protection blocks the push** with a message like:

```
remote: error: GH013: Repository rule violations found for refs/heads/...
remote: — GITHUB_TOKEN — azure_code_vulns.py:XX
```

5. Demo the bypass options:
   - **"It's used in tests"** — allows push, creates an alert marked as test
   - **"It's a false positive"** — allows push, creates a dismissed alert
   - **"I'll fix it later"** — allows push, creates an open alert

### Option B — Push a Secret Without Push Protection (Alert-Only Demo)

If push protection is disabled (or the secret type isn't covered by push protection):

1. Add a secret matching a known pattern to a file:

```python
# AWS Access Key (classic format — detected by secret scanning)
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
```

2. Push the commit
3. Navigate to **Security → Secret scanning** — an alert appears within minutes

### Known Secret Patterns That Trigger Alerts

GitHub secret scanning supports 200+ provider patterns. The ones most useful for demos:

| Secret Type | Example Format | Push Protection |
|---|---|---|
| GitHub PAT (classic) | `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` | Yes |
| GitHub PAT (fine-grained) | `github_pat_...` | Yes |
| AWS Access Key | `AKIA...` + secret key | Yes |
| Azure Storage Key | Base64 string with `==` suffix in context | Partial |
| Slack Bot Token | `xoxb-...` | Yes |
| Stripe Secret Key | `sk_live_...` | Yes |
| SendGrid API Key | `SG....` | Yes |
| Google API Key | `AIza...` | Yes |
| npm Token | `npm_...` | Yes |

### Existing Secrets in This Repo

The repo already contains these intentional secrets:

**In `azure_code_vulns.py`:**
- Slack Bot Token (`xoxb-...`)
- SendGrid API Key (`SG....`)
- Stripe Secret Key (`sk_live_...`)

**In `azure_insecure_services.py`:**
- Azure Storage Account Key
- Azure Client Secret
- SQL Server connection string with embedded password

### Custom Secret Patterns

For secrets that don't match a built-in pattern, you can create **custom patterns**:

1. Go to **Settings → Code security → Secret scanning → Custom patterns**
2. Define a regex, e.g. for internal API keys:
   - Pattern: `DEMO-KEY-[A-Za-z0-9]{32}`
   - Name: "Internal Demo API Key"
3. Add a matching secret to code and push — an alert is generated

---

## Tips for a Smooth Demo

- **Pre-run the CodeQL workflow** before the demo so alerts are already populated — avoids waiting for CI
- **Use a PR** for the code scanning portion so alerts appear inline in the diff (more visual impact)
- **Have the Security tab open** in a browser tab ready to show
- **Disable branch protection** on the demo branch so pushes aren't blocked by failing checks
- **Use push protection** for the secret scanning portion — the real-time block is the most impressive part
- **Prepare a "fix" commit** ahead of time so you can show how alerts auto-close when the issue is resolved
- **Show the API/SARIF integration** if the audience cares about CI/CD pipelines (CodeQL results are SARIF-based)

---

## Quick Reference — Alert Locations in GitHub UI

| Feature | Navigation Path |
|---|---|
| Code scanning alerts | **Security** → **Code scanning** |
| Secret scanning alerts | **Security** → **Secret scanning** |
| Dependabot alerts | **Security** → **Dependabot** |
| Push protection log | **Security** → **Secret scanning** → **Push protection** |
| Dependency graph | **Insights** → **Dependency graph** |
| Security overview (org) | **Organization** → **Security** tab |
| CodeQL workflow runs | **Actions** → **CodeQL** |