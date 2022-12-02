from ..app import app
from flask import render_template


@app.route("/compile")
def home():
    """Renders the entire Jinja template from templates folder"""
    return render_template("index.html")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return app.send_static_file("compiled_frontend/index.html")
