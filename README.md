
Bhaskar Reddy Appala
11:41 AM (1 minute ago)
to me

# 🛡️ SafeGuardian007 – Real-Time Screen Monitoring for Child Safety

## 🔍 Overview
**SafeGuardian007** is an intelligent screen monitoring tool built with Python to ensure children’s digital safety. It actively captures screen content, scans it for harmful or inappropriate keywords using OCR, and alerts parents in real-time via email while locking the screen until authorized.

## 🎯 Key Features
- **Real-time Screen Capture** with `ImageGrab`
- **Optical Character Recognition (OCR)** using `EasyOCR`
- **Harmful Content Detection** with predefined keyword filtering
- **Email Alert System** to notify parents with unlock codes
- **Lock Screen Overlay** with restricted access
- **Secure Unlock Mechanism** based on email code verification
- **System Tray Integration** using `PyStray`

## ⚙️ Tech Stack
- Python
- EasyOCR
- Tkinter
- Pillow (PIL)
- Smtplib
- PyStray
- ImageGrab
- NumPy

## 🚀 Getting Started
### 🔧 Prerequisites
```bash
pip install easyocr pystray pillow numpy
```

### ▶️ How to Run
```bash
python SafeGuardian007.py
```

### 📁 Folder Structure
```
├── SafeGuardian007.py
├── temp_screenshots/  # stores temporary screenshots
├── stopnow.txt        # optional emergency stop trigger
```

## 🔐 Security Highlights
- Screens are segmented into quadrants for accurate OCR analysis.
- Lock screen prevents access until the correct code is entered.
- Email alerts prevent parents from missing any harmful activity.
- Only predefined harmful keywords are flagged (customizable).

## 💡 Motivation
With children spending more time online, **SafeGuardian007** provides peace of mind to parents by continuously monitoring screen content and intervening when inappropriate or dangerous activity is detected.

> "Children's digital safety is in control. Parents can be relieved."

## 📬 Want to Contribute or Collaborate?
Feel free to fork the repo and enhance it with features like:
- AI-based content classification
- Remote access and parental dashboard
- Mobile app integration for alerts
