import os
import time
import json

from flask import Flask, render_template, render_template_string, request, redirect

app = Flask(__name__)

# Path to the transcripts folder
TRANSCRIPTS_FOLDER = os.path.join(os.getcwd(), 'transcripts')
with open("config.json", mode="r") as config_file:
    config = json.load(config_file)

ID = config["web_id"]
PASS = config["web_pass"]

auth_maps = {}

@app.route('/')
def index():
    if not check_auth(request.remote_addr):
        return render_template('auth.html')
    return redirect('/explorer')

# I know this is a bad way of checking for authentication
# but for a quick and dirty solution,
# it is good
@app.route('/auth/<user>/<password>')
def authenticate(user, password):
    if user == ID and password == PASS:
        auth_maps[request.remote_addr] = time.time()
    # auth_maps[user] = password
    return redirect('/')
    # return "Authentication successful", 200

@app.route('/explorer')
def explorer():
    if not  check_auth(request.remote_addr):
        return redirect('/')
    # Get a list of all .html files in the ./transcripts/ directory
    html_files = [f for f in os.listdir(TRANSCRIPTS_FOLDER) if f.endswith('.html')]

    # Pass the list of HTML files to the template
    return render_template('index.html', html_files=html_files)


@app.route('/transcripts/<filename>')
def show_transcript(filename):
    if not check_auth(request.remote_addr):
        return redirect('/')
    # Ensure the file exists and is in the transcripts folder
    filename_path: str = os.path.join(TRANSCRIPTS_FOLDER, filename)

    if not os.path.exists(filename_path) and filename.endswith('.html'):
        return "File not found", 404

    with open(filename_path, 'r') as f:
        content = f.read()

    return render_template_string(content)

def check_auth(ip):
    if ip not in auth_maps:
        return False
    return auth_maps.get(ip) > time.time() - 180 # 3 minutes of session on the same IP
