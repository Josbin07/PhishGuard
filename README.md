# 🎧 PhishGuard# 🎧 PhishGuard
### Web-Based Phishing Simulation & Security Awareness Platform

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Flask](https://img.shields.io/badge/Flask-3.1-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## 📌 Overview
PhishGuard is a web-based phishing simulation and security awareness platform built for authorized security testing within organizations. It allows administrators to create phishing campaigns, send simulated phishing emails, track recipient interactions, deliver security awareness training, and generate detailed PDF reports.

> ⚠️ **Disclaimer:** This tool is intended strictly for authorized security awareness testing and educational purposes. Unauthorized use against individuals or organizations without explicit consent is illegal and unethical.

---

## 🚀 Features
- 📧 Automated phishing email delivery via Gmail SMTP
- 🎯 Per-recipient unique tracking tokens
- 📊 Real-time event logging (email sent, link clicked, credentials submitted)
- 🖥️ Microsoft 365, IT Helpdesk & HR Portal phishing templates
- 🎓 Automatic security awareness training page for recipients who fall for the simulation
- 📄 Professional PDF report generation with charts and risk assessments
- 🌙 Dark / Light mode toggle
- ☁️ Deployed 24/7 on PythonAnywhere

---

## 🛠️ Tech Stack
| Component | Technology |
|-----------|-----------|
| Backend | Python 3.10, Flask 3.1 |
| Database | SQLite via SQLAlchemy |
| Frontend | Bootstrap 5.3, HTML5, CSS3, JavaScript |
| Email | Flask-Mail, Gmail SMTP (TLS Port 587) |
| Auth | Flask-Login, Bcrypt |
| PDF Reports | ReportLab, Matplotlib |
| Deployment | PythonAnywhere |

---

## ⚙️ Installation (Local)
```bash
# Clone the repository
git clone https://github.com/Josbin07/PhishGuar# 🎧 PhishGuard
### Web-Based Phishing Simulation & Security Awareness Platform

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Flask](https://img.shields.io/badge/Flask-3.1-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## 📌 Overview
PhishGuard is a web-based phishing simulation and security awareness platform built for authorized security testing within organizations. It allows administrators to create phishing campaigns, send simulated phishing emails, track recipient interactions, deliver security awareness training, and generate detailed PDF reports.

> ⚠️ **Disclaimer:** This tool is intended strictly for authorized security awareness testing and educational purposes. Unauthorized use against individuals or organizations without explicit consent is illegal and unethical.

---

## 🚀 Features
- 📧 Automated phishing email delivery via Gmail SMTP
- 🎯 Per-recipient unique tracking tokens
- 📊 Real-time event logging (email sent, link clicked, credentials submitted)
- 🖥️ Microsoft 365, IT Helpdesk & HR Portal phishing templates
- 🎓 Automatic security awareness training page for recipients who fall for the simulation
- 📄 Professional PDF report generation with charts and risk assessments
- 🌙 Dark / Light mode toggle
- ☁️ Deployed 24/7 on PythonAnywhere

---

## 🛠️ Tech Stack
| Component | Technology |
|-----------|-----------|
| Backend | Python 3.10, Flask 3.1 |
| Database | SQLite via SQLAlchemy |
| Frontend | Bootstrap 5.3, HTML5, CSS3, JavaScript |
| Email | Flask-Mail, Gmail SMTP (TLS Port 587) |
| Auth | Flask-Login, Bcrypt |
| PDF Reports | ReportLab, Matplotlib |
| Deployment | PythonAnywhere |

---

## ⚙️ Installation (Local)
```bash
# Clone the repository
git clone https://github.com/Josbin07/PhishGuard.git
cd PhishGuard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your settings

# Initialize database and run
python run.py
```

---

## 🔧 Environment Variables
Create a `.env` file with the following:
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///phishguard.db
APP_BASE_URL=http://localhost:5000
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

> 💡 Gmail requires an **App Password** — not your regular password. Enable 2FA and generate one at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

---

## 🌐 Live Demo
👉 [https://josbin.pythonanywhere.com](https://josbin.pythonanywhere.com)

**Login:**
- Email: `admin@phishguard.local`
- Password: `admin123`

---

## 📸 Screenshots
| Login Page | Dashboard |
|-----------|-----------|
| ![Login](app/static/screenshots/login.png) | ![Dashboard](app/static/screenshots/dashboard.png) |

---

## 👨‍💻 Author
**Josbin K S**
- OCSP Student — Offenso Hackers Academy, Trivandrum
- Trainer: Abhimanyu R
- GitHub: [@Josbin07](https://github.com/Josbin07)

---

## 📜 License
This project is licensed under the MIT License.
