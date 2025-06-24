from flask import Flask, request, render_template_string, redirect, url_for
from datetime import datetime, timedelta
import requests

app = Flask(__name__)
app.secret_key = 'secretkey'

# --- User credentials ---
users = {'admin': 'password123'}

# --- Lockout config ---
login_attempts = {}
LOCKOUT_THRESHOLD = 5
LOCKOUT_TIME = timedelta(minutes=5)

# --- Mailgun API Config ---
MAILGUN_API_KEY = 'c4fea02015bd374aa885229a1891e849-3d4b3a2a-6006dfbd'
MAILGUN_DOMAIN = 'sandbox1fe078946a3f49899c1a02525e53922c.mailgun.org'
ADMIN_EMAIL = 'mditcyber23@gmail.com'  # Email to receive lockout alerts

# --- Mailgun Email Function ---
def send_lockout_email(username):
    response = requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": f"Alert <mailgun@{MAILGUN_DOMAIN}>",
            "to": [ADMIN_EMAIL],
            "subject": "🚨 WiFi Security Alert 🚨",
            "text": f"Account '{username}' has been locked due to too many failed login attempts. Contact the AeroLink IT Support Team at for assistance in unlocking your account."
        }
    )
    print("✅ Mailgun Response:", response.status_code, response.text)

# --- Success page ---
@app.route('/success')
def success():
    return render_template_string("""
    <html><head><title>WiFi Login Success</title></head>
    <body style="background:#2b2b2b; text-align:center; padding:50px; color: #a85cf9;">
    <h1 style="color:#a85cf9;">Successfully Connected to WiFi</h1>
    <p style="color:white;">AeroLink</p>
    </body></html>
    """)

# --- Login page with lockout logic ---
@app.route('/', methods=['GET', 'POST'])
def login():
    username = 'admin'
    error = None

    if username not in login_attempts:
        login_attempts[username] = {'attempts': 0, 'lockout_time': None}

    lockout_info = login_attempts[username]
    if lockout_info['lockout_time'] and datetime.now() < lockout_info['lockout_time']:
        return render_template_string("""
            <html><head><title>WiFi Login</title></head>
            <body style="background:#1c1c1c; text-align:center; padding:50px; color: #a85cf9;">
            <h1 style="color:red;">🚫 Account Locked!</h1>
            <p>Try again after {{ time }}.</p>
            </body></html>
        """, time=lockout_info['lockout_time'].strftime("%H:%M:%S"))

    if request.method == 'POST':
        input_username = request.form['username']
        input_password = request.form['password']

        if input_username == username and input_password == users[username]:
            login_attempts[username] = {'attempts': 0, 'lockout_time': None}
            return redirect(url_for('success'))
        else:
            login_attempts[username]['attempts'] += 1
            if login_attempts[username]['attempts'] >= LOCKOUT_THRESHOLD:
                login_attempts[username]['lockout_time'] = datetime.now() + LOCKOUT_TIME
                send_lockout_email(username)  # Mailgun alert
                return render_template_string("""
                    <html><head><title>WiFi Login</title></head>
                    <body style="background:#1c1c1c; text-align:center; padding:50px; color: #a85cf9;">
                    <h1 style="color:red;">🚨 Account Locked!</h1>
                    <p>Admin notified. Try again after 5 minutes.</p>
                    </body></html>
                """)
            else:
                error = f"❌ Invalid credentials. Attempt {login_attempts[username]['attempts']}/{LOCKOUT_THRESHOLD}"

    return render_template_string("""
    <html>
    <head>
        <title>WiFi Login Portal</title>
        <style>
            body {
                background-color: #1c1c1c;
                font-family: 'Segoe UI', sans-serif;
                text-align: center;
                padding: 50px;
                color: #a85cf9;
            }
            .login-box {
                background: #2b2b2b;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 0 25px rgba(168, 92, 249, 0.6);
                max-width: 400px;
                margin: auto;
            }
            input[type="text"], input[type="password"] {
                width: 90%;
                padding: 14px;
                margin: 12px 0;
                border: none;
                border-radius: 10px;
                background: #3a3a3a;
                color: #fff;
            }
            input[type="submit"] {
                background-color: #a85cf9;
                color: white;
                padding: 14px 20px;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                width: 95%;
                font-size: 16px;
            }
            input[type="submit"]:hover {
                background-color: #923ff5;
            }
            .error { color: #ff4d4d; }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>AeroLink</h2>
            <form method="post">
                <input type="text" name="username" placeholder="Username" required><br>
                <input type="password" name="password" placeholder="Password" required><br>
                <input type="submit" value="Login">
            </form>
            {% if error %}
                <p class="error">{{ error }}</p>
            {% endif %}
        </div>
    </body>
    </html>
    """, error=error)

if __name__ == '__main__':
    app.run(debug=True)

