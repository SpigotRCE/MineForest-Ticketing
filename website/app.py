import os

from flask import Flask, render_template, render_template_string

app = Flask(__name__)

# Path to the transcripts folder
TRANSCRIPTS_FOLDER = os.path.join(os.getcwd(), 'transcripts')


@app.route('/')
def index():
    # Get a list of all .html files in the ./transcripts/ directory
    html_files = [f for f in os.listdir(TRANSCRIPTS_FOLDER) if f.endswith('.html')]

    # Pass the list of HTML files to the template
    return render_template('index.html', html_files=html_files)


@app.route('/transcripts/<filename>')
def show_transcript(filename):
    # Ensure the file exists and is in the transcripts folder
    filename_path: str = os.path.join(TRANSCRIPTS_FOLDER, filename)

    if not os.path.exists(filename_path) and filename.endswith('.html'):
        return "File not found", 404

    with open(filename_path, 'r') as f:
        content = f.read()

    return render_template_string(content)
