from ..app import app
from flask import send_from_directory

# Path for our main Svelte page
@app.route("/")
def base():
    return send_from_directory('../client/dist', 'index.html')

@app.route("/<path:path>")
def spa_path(path):
    """Compiles the HTML then returns it as a static file to allow for SPA paths to work."""
    return send_from_directory("../client/dist", path)
    