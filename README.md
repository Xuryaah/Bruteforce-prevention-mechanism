AeroLink — WiFi Login Portal

A simple Flask-based WiFi login portal with account lockout and Mailgun alerting for repeated failed login attempts. This repo includes a minimal UI for login and a success page showing WiFi settings. Built for demonstration / internal tooling and not ready for production without following the security recommendations below.

Table of Contents

Demo

Features

Requirements

Installation

Configuration

Running the app

How the lockout works

Mailgun email alerts

Security notes & recommended improvements

Contributing

License

Demo

This app exposes two endpoints:

GET / — login page

POST / — submit credentials

GET /success — WiFi settings dashboard shown after successful login

When an account receives LOCKOUT_THRESHOLD consecutive failed login attempts, it is locked for LOCKOUT_TIME and an alert email is sent to the configured admin address via Mailgun.

Features

Minimal Flask login page with styled UI (dark theme)

Per-account tracking of failed login attempts

Automatic account lockout after configurable threshold

Mailgun integration to notify an admin on lockout

Simple success page showing WiFi settings (demo purposes)

Requirements

Python 3.8+

pip

Suggested Python packages (see requirements.txt below):

Flask>=2.0
requests>=2.25
python-dotenv>=0.21  # optional, for loading .env in development

Installation

Clone the repository:

git clone https://github.com/YOUR_USERNAME/aerolink.git
cd aerolink


Create and activate a virtual environment (recommended):

python -m venv venv
# Linux / macOS
source venv/bin/activate
# Windows (PowerShell)
venv\Scripts\Activate.ps1


Install dependencies:

pip install -r requirements.txt


If you don't have a requirements.txt, create one with:

Flask
requests
python-dotenv

Configuration

Important configuration is at the top of the Flask file (or you can use environment variables).

Example .env (recommended — do not commit):

FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=change_this_to_a_random_string
MAILGUN_API_KEY=your-mailgun-api-key
MAILGUN_DOMAIN=mg.yourdomain.com
ADMIN_EMAIL=you@yourdomain.com
LOCKOUT_THRESHOLD=5
LOCKOUT_TIME_MINUTES=5


If you prefer environment variables in code, modify the app to read from os.environ or use python-dotenv to load .env.

Credentials

The sample code stores a single user in the users dict:

users = {'admin': 'password123'}


Do not keep plaintext credentials in production. See Security Notes below.

Running the app

Development (works out of the box):

export FLASK_APP=app.py
export FLASK_ENV=development
flask run


Or:

python app.py


Open http://127.0.0.1:5000/ in your browser.

How the lockout works

login_attempts keeps a per-username record:

login_attempts[username] = { 'attempts': X, 'lockout_time': datetime or None }


Each failed login increments attempts.

When attempts >= LOCKOUT_THRESHOLD:

lockout_time is set to datetime.now() + LOCKOUT_TIME.

Mailgun alert is sent to ADMIN_EMAIL.

Login is rejected for that user until lockout_time passes.

Mailgun email alerts

The app uses Mailgun's HTTP API to post a simple alert when an account is locked:

response = requests.post(
    f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
    auth=("api", MAILGUN_API_KEY),
    data={ ... }
)


Notes:

You must supply MAILGUN_API_KEY, MAILGUN_DOMAIN, and ADMIN_EMAIL.

In development you may want to stub out or disable the notifier to avoid sending test emails. Example:

def send_lockout_email(username):
    if MAILGUN_API_KEY.startswith("test-") or FLASK_ENV == "development":
        print("[DEV] Lockout email suppressed:", username)
        return
    # ... real request

Security notes & recommended improvements

This project is a demo. If you intend to use it beyond development, do not deploy as-is. Recommended hardening:

Never store plaintext passwords. Use a password hashing library (e.g., bcrypt, passlib) and store hashed passwords.

Move secrets out of source code. Use environment variables, secret managers, or .env files excluded from git.

Use HTTPS in production. Never expose login pages over plain HTTP.

Rate limiting & IP throttling. Add per-IP rate limiting (e.g., via Flask-Limiter) to prevent brute force attacks beyond per-account lockout.

Account unlock admin flow. Instead of auto-unlock only after time, consider an admin override and/or notification with more context.

CSRF protection. Use Flask-WTF or other CSRF protections for forms.

Session management. Use secure cookie settings: SESSION_COOKIE_SECURE=True, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax'.

Audit & logging. Centralized logging for security events and failed attempts.

Input validation & sanitization. Ensure all inputs are validated and escaped.

Mail validation. Verify that Mailgun responses are checked for success/failure and handle retries/backoff.

Example requirements.txt
Flask>=2.0
requests>=2.25
python-dotenv>=0.21
Flask-Limiter>=2.0  # optional, for rate limiting
bcrypt>=4.0  # optional, for password hashing

Contributing

Fork the repository

Create a feature branch: git checkout -b feat/my-change

Commit: git commit -m "Add my feature"

Push: git push origin feat/my-change

Open a Pull Request

Please open issues for bugs or security concerns.

License

This project is provided as-is for educational/demo purposes. Add an appropriate open-source license (e.g., MIT) if you want to share publicly.
