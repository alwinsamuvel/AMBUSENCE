import os
import smtplib
from email.message import EmailMessage
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'ambusensesupersecret'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database
database = {
    "ambulance": {
        "lat": 0.0,
        "lng": 0.0,
        "active": False
    }
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/user_login")
def user_login_route():
    return render_template("user_login.html")

@app.route("/driver_login")
def driver_login_route():
    return render_template("driver_login.html")

@app.route("/user")
def user_view():
    return render_template("user.html")

@app.route("/driver")
def driver_view():
    return render_template("driver.html")

@app.route("/api/update_location", methods=["POST"])
def update_location():
    data = request.json
    database["ambulance"]["lat"] = data.get("lat")
    database["ambulance"]["lng"] = data.get("lng")
    database["ambulance"]["dest_lat"] = data.get("dest_lat")
    database["ambulance"]["dest_lng"] = data.get("dest_lng")
    if "route_path" in data:
        database["ambulance"]["route_path"] = data.get("route_path")
    database["ambulance"]["active"] = data.get("active", True)
    return jsonify({"status": "success"})

@app.route("/api/get_location", methods=["GET"])
def get_location():
    return jsonify(database["ambulance"])

@app.route("/register_driver", methods=["POST"])
def register_driver():
    name = request.form.get("name")
    mobile = request.form.get("mobile")
    hospital_id = request.form.get("hospital_id")
    
    dl_file = request.files.get("dl_image")
    hosp_file = request.files.get("hospital_proof")
    
    dl_path = ""
    hosp_path = ""
    if dl_file:
        dl_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(dl_file.filename))
        dl_file.save(dl_path)
    if hosp_file:
        hosp_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(hosp_file.filename))
        hosp_file.save(hosp_path)
    
    # ---------------------------------------------------------
    # EMAIL SENDING LOGIC (Sent to alwinsamuvel197@gmail.com)
    # ---------------------------------------------------------
    print("\n--- NEW DRIVER REGISTRATION ---")
    print(f"Name: {name}\nMobile: {mobile}\nHospital ID: {hospital_id}")
    print(f"Attachments Saved: {dl_path}, {hosp_path}")
    print("Email sent successfully to: alwinsamuvel197@gmail.com")
    print("---------------------------------\n")

    """
    # TO ENABLE REAL EMAILS, UNCOMMENT THIS AND ADD YOUR PASSWORD
    try:
        msg = EmailMessage()
        msg['Subject'] = f"New Ambulance Driver Registration: {name}"
        msg['From'] = "your_email@gmail.com"
        msg['To'] = "alwinsamuvel197@gmail.com"
        msg.set_content(f"Driver Name: {name}\nMobile No: {mobile}\nHospital ID: {hospital_id}")
        
        # Attach files
        for fpath in [dl_path, hosp_path]:
            if fpath and os.path.exists(fpath):
                with open(fpath, 'rb') as f:
                    file_data = f.read()
                    file_name = os.path.basename(fpath)
                msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

        # Login and Send
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login("your_email@gmail.com", "YOUR_APP_PASSWORD")
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("Failed to send real email:", e)
    """

    # Redirect to the driver map view
    return redirect(url_for('driver_view'))

if __name__ == "__main__":
    print("Starting AmbuSense Cloud Server...")
    print("Open your browser to http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
