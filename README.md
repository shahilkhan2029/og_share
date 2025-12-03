# 📂 Local File Share — Python + BAT Launcher

A simple and powerful **local file-sharing web app** that lets you transfer files between your **laptop and mobile device** directly over Wi-Fi.  
This version runs **100% automatically from a `.bat` file** — no commands needed.

The server launches in your default browser, shows you a QR code for mobile connection, and provides a clean drag-and-drop interface for file uploads and downloads.

This README covers the usage of these two files:

- **og_share.py** — the main Python web server  
- **og_share.bat** — the Windows launcher that starts the server automatically

---

# 🚀 Features

### ✅ 1. One-Click Start (BAT File)
Just double-click `og_share.bat` — it launches:
- the Python server  
- your default browser  
- the full web interface  

No terminal commands required.

---

### 📱 2. Mobile Pairing via QR Code
The web UI shows a **QR code** that automatically links your phone to the server.

Scan → Start sharing instantly.

---

### 📤 3. Drag & Drop Uploads (With Progress %)
You can:
- drag and drop files  
- or click to choose files  

The UI shows:
- progress bar  
- percentage uploaded  
- “% Shared” status  
- success message after upload

---

### 📁 4. Automatic Shared Folder
A folder named **`shared/`** is created next to the script on first run.

Everything uploaded from any device is saved inside this folder.

You can also manually place files there — they will appear in the UI.

---

### 🗑️ 5. Delete Files From UI
Files in the `shared/` folder can be deleted with a single button in the interface.

---

### 🛑 6. Stop Server From Browser
A **Stop Server** button is available in the top-right corner.

Click → Server shuts down safely → Browser shows "Server stopped".

---

### 🔧 7. Auto-Install Dependencies
If packages are missing (`flask`, `qrcode`, `pillow`):
- The script installs them automatically  
- Then restarts itself  

No manual installation required.

---

# 📦 Included Files

### **1. og_share.py**
The main file-sharing server.  
Handles:
- QR generation  
- UI rendering  
- Uploads with progress  
- Downloads  
- File deletion  
- Secure path handling  
- Remote shutdown  

📄 Source: `og_share.py`

---

### **2. og_share.bat**
Windows launcher for the project.

Double-click to:
- run the Python script  
- launch the browser  
- auto-start the server  

📄 Source: `og_share.bat`

---

# 🖥️ How to Run

### ✔️ Step 1 — Make Sure Python 3 Is Installed
```
python --version
```
If not installed, get it from python.org.

---

### ✔️ Step 2 — Place Files Together
```
yourfolder/
│
├── og_share.py
└── og_share.bat
```

---

### ✔️ Step 3 — Double-Click `og_share.bat`
The app will:
1. Start the server  
2. Open your browser  
3. Show your server URL  
4. Display the QR code to scan with your phone  

That's it. No commands needed.

---

# 📱 How to Use (Laptop ↔ Mobile)

### **On Your Laptop**
- Drag & drop to upload  
- Download files  
- Delete unwanted files  
- Stop server from UI  

### **On Your Phone**
- Scan QR  
- Same interface opens  
- Upload files to laptop  
- Download files from laptop  

Everything works instantly over Wi-Fi.

---

# 📁 File Storage

All files go into:

```
shared/
```

Created automatically next to the script.

- Files inside appear in browser  
- Removing them removes them from UI  

---

# ⚠️ Security Notes

- Runs on **local Wi-Fi** only  
- Anyone with the IP **on the same network** can access files  
- Avoid using this on public Wi-Fi  
- Intended for personal / trusted environments  

---

# 🛠️ Troubleshooting

### ❓ Browser doesn’t open?
Visit manually:
```
http://<your-ip>:8000/
```

### ❓ Port 8000 is busy?
Change port inside `og_share.py`.

### ❓ Modules not installed?
Run:
```
pip install flask qrcode pillow
```

---

# 📜 License

Free to use. Free to modify. Free to distribute.

---

# ❤️ Author

Made with ❤️ by **Shahil Khan**  
YouTube Channel 👉 https://www.youtube.com/@OfGuru

