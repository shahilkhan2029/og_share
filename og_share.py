#!/usr/bin/env python3
"""share_web_app.py
Single-file Flask web app for easy file sharing with mobile QR and a polished UI.

Usage:
    python share_web_app.py            # show instructions and QR preview (no server)
    python share_web_app.py runserver  # start server (blocks)
    python share_web_app.py runserver --open  # start server and open browser automatically
"""

import os
import sys
import socket
import threading
import subprocess
import base64
import io
import argparse
import time
from pathlib import Path

# --- Dependency Management ---
REQUIRED_PACKAGES = {
    "flask": "flask",
    "qrcode": "qrcode",
    "PIL": "pillow"
}

def ensure_requirements():
    missing = []
    for import_name, pip_name in REQUIRED_PACKAGES.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pip_name)
    
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print("Attempting to install via pip...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
            print("Installation successful. Restarting script...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            print(f"Automatic install failed: {e}") 
            sys.exit(1)

ensure_requirements()

from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string, abort, jsonify
from werkzeug.utils import secure_filename
import qrcode

# --- Configuration ---
PORT = 8000
SHARE_DIR = Path(__file__).parent / "shared"
SHARE_DIR.mkdir(exist_ok=True)

# --- Helpers ---
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def make_qr_base64(url):
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    data = base64.b64encode(bio.read()).decode('ascii')
    return "data:image/png;base64," + data

def is_safe_path(filename):
    try:
        file_path = (SHARE_DIR / filename).resolve()
        return file_path.parent == SHARE_DIR.resolve()
    except Exception:
        return False

# --- Flask App ---
app = Flask(__name__)

INDEX_HTML = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Share — Local File Share</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body{padding-top:30px;background:#f7f7fb}
.share-card{max-width:1000px;margin:auto}
.file-row{display:flex;justify-content:space-between;align-items:center;padding:8px 12px;border-bottom:1px solid #eee}
.drop-area{border:2px dashed #ced4da;border-radius:8px;padding:18px;text-align:center;background:#fff;cursor:pointer;transition:border-color 0.2s}
.drop-area:hover{border-color:#0d6efd}
.small{font-size:.85rem;color:#666}
</style>
</head><body>
<div class="container share-card">
  <div class="card shadow-sm">
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <div>
          <h4 class="mb-0">Share — Local File Share</h4>
          <div class="small">Share files between laptop and phone on the same Wi‑Fi.</div>
        </div>
        <div class="text-end">
          <div class="d-flex align-items-center gap-3">
            <div>
                <div class="small">Server URL</div>
                <div><a href="{{ url }}">{{ url }}</a></div>
            </div>
            <button onclick="stopServer()" class="btn btn-outline-danger btn-sm">Stop Server</button>
          </div>
        </div>
      </div>

      <div class="row g-3">
        <div class="col-md-5">
          <div class="card p-3 mb-3">
            <div class="small mb-2">Scan QR to open on mobile</div>
            <div class="text-center">
              <img src="{{ qr }}" alt="QR code" style="max-width:220px" class="img-fluid border rounded" />
            </div>
            <div class="small text-muted mt-2">Scan with your phone camera or QR app.</div>
          </div>

          <div class="card p-3">
            <div class="small mb-2">Upload files (drag & drop or click)</div>
            <div id="drop" class="drop-area mb-2">Drop files here or click to choose</div>
            <input id="fileInput" type="file" multiple style="display:none" />
            
            <div id="progressContainer" class="mt-3" style="display:none;">
                <div class="d-flex justify-content-between small mb-1">
                    <span id="uploadStatusText">Starting...</span>
                    <span id="percentText">0%</span>
                </div>
                <div class="progress" style="height: 10px;">
                    <div id="progressBar" class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 0%"></div>
                </div>
            </div>

            <div id="finalStatus" class="small text-success mt-2"></div>
          </div>
        </div>

        <div class="col-md-7">
          <div class="card p-3">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <div><strong>Shared files</strong></div>
              <div class="small text-muted">/{{ shared_name }}</div>
            </div>
            <div id="filesList">
              {% for f in files %}
                <div class="file-row">
                  <div style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:60%"><a href="/files/{{ f }}">{{ f }}</a></div>
                  <div class="small text-muted">{{ files_meta[f]|default('') }}</div>
                  <div>
                    <a class="btn btn-sm btn-outline-primary" href="/files/{{ f }}" download>Down</a>
                    <button class="btn btn-sm btn-outline-danger ms-1" data-f="{{ f }}" onclick="deleteFile(event,this)">Del</button>
                  </div>
                </div>
              {% else %}
                <div class="small text-muted mt-2">No files yet — upload something.</div>
              {% endfor %}
            </div>
          </div>
        </div>
      </div>

    </div>
    <div class="card-footer small text-muted text-center">Tip: Keep this page open on your laptop while scanning from phone.</div>
  </div>
</div>

<script>
const drop = document.getElementById('drop');
const fileInput = document.getElementById('fileInput');
const progressContainer = document.getElementById('progressContainer');
const progressBar = document.getElementById('progressBar');
const uploadStatusText = document.getElementById('uploadStatusText');
const percentText = document.getElementById('percentText');
const finalStatus = document.getElementById('finalStatus');

drop.addEventListener('click', ()=> fileInput.click());
drop.addEventListener('dragover', e=>{ e.preventDefault(); drop.style.borderColor='#0d6efd'; drop.style.backgroundColor='#f8f9fa'; });
drop.addEventListener('dragleave', e=>{ e.preventDefault(); drop.style.borderColor=''; drop.style.backgroundColor='#fff'; });
drop.addEventListener('drop', async e=>{
  e.preventDefault();
  drop.style.borderColor='';
  drop.style.backgroundColor='#fff';
  const files = Array.from(e.dataTransfer.files);
  uploadFiles(files);
});
fileInput.addEventListener('change', ()=>{ uploadFiles(Array.from(fileInput.files)); fileInput.value=null; });

function uploadFiles(files){
  if(files.length===0) return;

  progressContainer.style.display = 'block';
  progressBar.style.width = '0%';
  percentText.textContent = '0%';
  uploadStatusText.textContent = 'Uploading ' + files.length + ' file(s)...';
  finalStatus.textContent = '';

  const form = new FormData();
  files.forEach(f=> form.append('file', f));

  const xhr = new XMLHttpRequest();
  xhr.open('POST', '/upload', true);

  xhr.upload.onprogress = function(e) {
    if (e.lengthComputable) {
      const percentComplete = Math.round((e.loaded / e.total) * 100);
      progressBar.style.width = percentComplete + '%';
      percentText.textContent = percentComplete + '%';
      uploadStatusText.textContent = percentComplete + '% Shared';
    }
  };

  xhr.onload = function() {
    if (xhr.status === 200) {
      progressBar.style.width = '100%';
      percentText.textContent = '100%';
      uploadStatusText.textContent = 'Processing...';
      setTimeout(() => {
          finalStatus.textContent = 'Upload complete!';
          progressContainer.style.display = 'none';
          location.reload(); 
      }, 800);
    } else {
      uploadStatusText.textContent = 'Error';
      finalStatus.textContent = 'Upload failed.';
    }
  };

  xhr.onerror = function() {
    uploadStatusText.textContent = 'Error';
    finalStatus.textContent = 'Network error occurred.';
  };

  xhr.send(form);
}

async function deleteFile(e, el){
  e.preventDefault();
  const f = el.getAttribute('data-f');
  if(!confirm('Delete ' + f + ' ?')) return;
  try{
    const res = await fetch('/delete/' + encodeURIComponent(f));
    if(res.ok) location.reload();
  }catch(err){ console.error(err); alert('Delete failed'); }
}

async function stopServer() {
    if(!confirm("Are you sure you want to stop the server? This will close the connection for everyone.")) return;
    try {
        await fetch('/shutdown', {method: 'POST'});
        document.body.innerHTML = '<div style="display:flex;justify-content:center;align-items:center;height:100vh;flex-direction:column;"><h2>Server Stopped</h2><p>You can close this tab now.</p></div>';
    } catch(e) {
        alert("Failed to stop server or server already stopped.");
    }
}
</script>
</body></html>
"""

def get_file_meta():
    files = sorted(x.name for x in SHARE_DIR.iterdir() if x.is_file() and not x.name.startswith('.'))
    files_meta = {}
    for f in files:
        try:
            s = (SHARE_DIR / f).stat().st_size
            files_meta[f] = (str(round(s/1024,1)) + ' KB') if s < 1024*1024 else (str(round(s/1024/1024,2)) + ' MB')
        except Exception:
            files_meta[f] = ''
    return files, files_meta

@app.route('/_files_json')
def files_json():
    files, meta = get_file_meta()
    return jsonify(files=files, meta=meta)

@app.route('/')
def index():
    ip = get_local_ip()
    url = f"http://{ip}:{PORT}/"
    qr = make_qr_base64(url)
    files, files_meta = get_file_meta()
    return render_template_string(INDEX_HTML, qr=qr, url=url, files=files, shared_name=SHARE_DIR.name, files_meta=files_meta)

@app.route('/files/<path:filename>')
def files_route(filename):
    safe_path = SHARE_DIR / filename
    if not is_safe_path(filename) or not safe_path.exists() or not safe_path.is_file():
        abort(404)
    return send_from_directory(str(SHARE_DIR), filename, as_attachment=False)

@app.route('/upload', methods=['POST'])
def upload():
    uploaded = request.files.getlist('file')
    for f in uploaded:
        if not f or f.filename == '':
            continue
        fn = secure_filename(f.filename)
        target = SHARE_DIR / fn
        f.save(str(target))
    return redirect(url_for('index'))

@app.route('/delete/<path:filename>')
def delete(filename):
    if is_safe_path(filename):
        p = SHARE_DIR / filename
        if p.exists() and p.is_file():
            p.unlink()
    return redirect(url_for('index'))

@app.route('/shutdown', methods=['POST'])
def shutdown():
    def kill_server():
        time.sleep(1) # Wait for response to be sent
        print("Server shutting down per user request.")
        os._exit(0) # Force kill process
    
    threading.Thread(target=kill_server).start()
    return "Shutting down..."

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', nargs='?', choices=['runserver'], help='Start the server')
    parser.add_argument('--open', action='store_true', help='Open browser automatically')
    args = parser.parse_args()

    ip = get_local_ip()
    url = f"http://{ip}:{PORT}/"
    
    print("\n" + "="*40)
    print(f" SHARE WEB APP")
    print("="*40)
    print(f" Folder: {SHARE_DIR.resolve()}")
    print(f" URL:    {url}")
    print("-" * 40)

    if args.cmd == 'runserver':
        print("Server running... (Press Ctrl+C to stop)")
        def run_app():
            app.run(host='0.0.0.0', port=PORT, threaded=True, debug=False)

        t = threading.Thread(target=run_app, daemon=True)
        t.start()
        
        if args.open:
            import webbrowser
            time.sleep(1)
            webbrowser.open(url)
        
        try:
            while t.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            print('\nStopping server...')
    else:
        print("QR Code preview generated. To run server, use:")
        print("    python share_web_app.py runserver")

if __name__ == '__main__':
    main()