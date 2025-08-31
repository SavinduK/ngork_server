import os
from flask import Flask, request, redirect, send_from_directory, render_template_string
from pyngrok import ngrok,conf
import qrcode
import qrcode.console_scripts  # for ASCII output

UPLOAD_FOLDER = "uploads"
PORT = 5000

# Create upload folder if missing
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
conf.get_default().auth_token = "<YOUR_AUTH_TOKEN>"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Simple HTML template
HTML = """
<!doctype html>
<title>File Share</title>
<h1>Upload a File</h1>
<form method=post enctype=multipart/form-data>
  <input type=file name=file>
  <input type=submit value=Upload>
</form>
<hr>
<h2>Files:</h2>
<ul>
  {% for file in files %}
    <li><a href="{{ url_for('download_file', filename=file) }}">{{ file }}</a></li>
  {% endfor %}
</ul>
"""

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)
            return redirect("/")
    files = os.listdir(app.config["UPLOAD_FOLDER"])
    return render_template_string(HTML, files=files)

@app.route("/files/<filename>")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)


if __name__ == "__main__":
    # Start ngrok tunnel
    public_url = ngrok.connect(PORT).public_url
    print("\n🌍 Public URL:", public_url)

    # Generate QR code (ASCII in terminal)
    qr = qrcode.QRCode()
    qr.add_data(public_url)
    qr.make(fit=True)

    print("\n📱 Scan this QR Code:\n")
    qr.print_ascii(invert=True)  # ASCII QR in terminal

    # Run the server
    app.run(port=PORT)
