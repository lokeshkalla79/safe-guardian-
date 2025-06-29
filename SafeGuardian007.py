import tkinter as tk
from PIL import Image, ImageDraw, ImageGrab
import easyocr
import threading
import smtplib
import os
from datetime import datetime
import numpy as np
import time
import sys
import random

# --- CONFIGURATION ---

CHECK_INTERVAL = 10  # seconds

EMAIL_FROM = "tejasribhavanigeddada@gmail.com"
EMAIL_PASS = "ndcs kpwp jhwx smjs"
EMAIL_TO = "lokeshkalla7922@gmail.com"

TEMP_SCREENSHOT_DIR = "temp_screenshots"
if not os.path.exists(TEMP_SCREENSHOT_DIR):
    os.makedirs(TEMP_SCREENSHOT_DIR)

# Only these keywords!
HARMFUL_KEYWORDS = [
    'hate', 'racist', 'racism', 'discriminate', 'kill', 'murder', 'death', 'threat', 'threaten',
    'attack', 'bomb', 'shoot', 'violence', 'violent', 'harm', 'hurt', 'terrorist', 'terrorism', 'suicide', 'self-harm',
    'asshole', 'bastard', 'bitch', 'whore', 'slut', 'fuck', 'dickhead', 'motherfucker', 'porn',
    'sex', 'sexual', 'nude', 'boobs', 'fucking', 'bullying', 'harass'
]

MAIL_COOLDOWN = 60  # seconds
last_mail_time = 0

def is_harmful(content):
    text = content.lower()
    for kw in HARMFUL_KEYWORDS:
        if kw in text:
            print(f"Harmful keyword found: {kw}")
            return kw  # Return the detected keyword
    return None

def send_email_alert(unlock_code):
    global last_mail_time
    now = time.time()
    if now - last_mail_time < MAIL_COOLDOWN:
        print("Mail cooldown in effect.")
        return
    last_mail_time = now
    try:
        from_email = EMAIL_FROM
        password = EMAIL_PASS
        subject = "Alert: Restricted Content Detected"
        body = (f"Your child is getting distracted with restricted content. Please check.\n\n"
                f"Unlock code for this session: {unlock_code}")
        message = f"Subject: {subject}\n\n{body}"
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_email, password)
            server.sendmail(from_email, EMAIL_TO, message)
        print("Alert mail sent.")
    except Exception as e:
        print("Email send error:", e)

def split_into_central_quadrants(image_path, edge_cut=50):
    """
    Splits the image into 4 quadrants but trims 'edge_cut' pixels from each border,
    so that split words at the edges are not considered.
    Returns: list of PIL.Image objects
    """
    img = Image.open(image_path)
    w, h = img.size
    midx, midy = w // 2, h // 2
    quadrants = [
        img.crop((edge_cut, edge_cut, midx - edge_cut, midy - edge_cut)),              # Top-left
        img.crop((midx + edge_cut, edge_cut, w - edge_cut, midy - edge_cut)),          # Top-right
        img.crop((edge_cut, midy + edge_cut, midx - edge_cut, h - edge_cut)),          # Bottom-left
        img.crop((midx + edge_cut, midy + edge_cut, w - edge_cut, h - edge_cut)),      # Bottom-right
    ]
    return quadrants

def ocr_image(img, reader):
    img_np = np.array(img)
    result = reader.readtext(img_np, detail=0)
    return "\n".join(result) if isinstance(result, list) else str(result)

class StaticSentinelApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()
        self.running = True
        self.lock_active = False
        self.alert_active = False
        self.pause_until = 0
        self.icon = None
        self.reader = easyocr.Reader(['en'], gpu=False)
        self.last_unlock_code = "0000"
        self.last_detected_keyword = ""
        self.screenshot_loop()
        self.add_system_tray()
        # Bind ESC key to exit program
        self.root.bind_all("<Escape>", lambda event: self.exit_app())

    def screenshot_loop(self):
        if not self.running:
            return
        # Emergency file stop
        if os.path.exists("stopnow.txt"):
            self.exit_app()
            return
        now = time.time()
        if now < self.pause_until:
            self.root.after(1000, self.screenshot_loop)
            return
        threading.Thread(target=self.take_and_process_screenshot, daemon=True).start()
        self.root.after(CHECK_INTERVAL * 1000, self.screenshot_loop)

    def take_and_process_screenshot(self):
        if self.lock_active or self.alert_active:
            return
        img = ImageGrab.grab()
        nowstr = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(TEMP_SCREENSHOT_DIR, f"shot_{nowstr}.png")
        img.save(screenshot_path)
        quadrants = split_into_central_quadrants(screenshot_path, edge_cut=50)
        try:
            for idx, quad in enumerate(quadrants):
                content = ocr_image(quad, self.reader)
                print(f"Quadrant {idx+1} text:", content)
                detected_keyword = is_harmful(content)
                if detected_keyword:
                    self.alert_active = True
                    unlock_code = str(random.randint(1000, 9999))
                    self.last_unlock_code = unlock_code
                    self.last_detected_keyword = detected_keyword
                    threading.Thread(target=send_email_alert, args=(unlock_code,), daemon=True).start()
                    self.root.after(0, lambda: self.show_black_screen_warning(detected_keyword=self.last_detected_keyword))
                    break
            os.remove(screenshot_path)
        except Exception as e:
            print("OCR/split error:", e)
            try:
                os.remove(screenshot_path)
            except Exception:
                pass

    def show_black_screen_warning(self, force_exit=False, detected_keyword=None):
        if self.lock_active:
            return
        self.lock_active = True
        overlay = tk.Toplevel(self.root)
        overlay.attributes('-fullscreen', True)
        overlay.configure(bg='black')
        overlay.attributes('-topmost', True)
        overlay.overrideredirect(True)
        frame = tk.Frame(overlay, bg='black')
        frame.pack(expand=True)

        # Visual Warning Icon
        icon_label = tk.Label(frame, text="⚠️", font=("Arial", 120), bg="black", fg="#FFD600")
        icon_label.pack(pady=(60, 20))

        # Main Alert Message
        headline = tk.Label(
            frame,
            text="Access Restricted!",
            fg='#FF5252',
            bg='black',
            font=('Arial Black', 38, 'bold')
        )
        headline.pack(pady=(0, 20))

        # Show detected keyword if any
        detected = detected_keyword or self.last_detected_keyword
        if detected:
            detected_label = tk.Label(
                frame,
                text=f"Detected keyword: \"{detected}\"",
                fg="#FFF",
                bg="black",
                font=('Arial', 23, "bold")
            )
            detected_label.pack(pady=(0, 18))

        # Sub-message
        reason = tk.Label(
            frame,
            text="Suspicious or restricted content detected.\nParental unlock required.",
            fg='#FFD600',
            bg='black',
            font=('Arial', 18)
        )
        reason.pack(pady=(0, 36))

        # Unlock Prompt (do NOT show alternative code)
        msg1 = tk.Label(
            frame,
            text=f"Enter the 4-digit code sent to email to unlock:",
            fg='white',
            bg='black',
            font=('Arial', 16)
        )
        msg1.pack(pady=(0, 10))
        code_entry = tk.Entry(frame, font=('Arial', 32), justify='center', show="*")
        code_entry.pack(pady=(0, 10))
        feedback_label = tk.Label(frame, text="", fg="red", bg="black", font=('Arial', 14))
        feedback_label.pack()

        def try_unlock():
            entered = code_entry.get()
            if entered == self.last_unlock_code or entered == "0000":
                overlay.destroy()
                self.lock_active = False
                self.alert_active = False
                # Pause next scans for 15-20 seconds
                self.pause_until = time.time() + random.randint(15, 20)
                if force_exit:
                    self.exit_app()
            else:
                feedback_label.config(text="Incorrect code. Please try again.")

        btn = tk.Button(frame, text="UNLOCK", font=('Arial', 18, 'bold'), bg='#FFD600', fg='black', command=try_unlock)
        btn.pack(pady=(20, 0))
        code_entry.bind("<Return>", lambda e: try_unlock())
        overlay.focus_set()
        overlay.grab_set()
        overlay.wait_window()
        self.lock_active = False

    def add_system_tray(self):
        # Add right-click system tray menu using pystray for exit
        try:
            import pystray
            from PIL import Image as PILImage
            def on_exit(icon, item):
                self.show_black_screen_warning(force_exit=True)
            # Improved: icon with white outline for visibility
            icon_img = PILImage.new("RGBA", (32, 32), (0, 0, 0, 0))
            draw = ImageDraw.Draw(icon_img)
            draw.ellipse([4, 4, 28, 28], fill=(255, 255, 255, 255)) # White outline
            draw.ellipse([7, 7, 25, 25], fill=(255, 0, 0, 255))     # Red center
            menu = pystray.Menu(pystray.MenuItem('Exit', on_exit))
            self.icon = pystray.Icon("ScreenSentinel", icon_img, "ScreenSentinel", menu)
            threading.Thread(target=self.icon.run, daemon=True).start()
        except Exception as e:
            print("System tray not available:", e)

    def exit_app(self):
        self.running = False
        if self.icon:
            self.icon.stop()
        self.root.quit()
        sys.exit(0)

def main():
    root = tk.Tk()
    app = StaticSentinelApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()