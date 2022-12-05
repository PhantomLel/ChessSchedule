from ..app import app
from flask import render_template


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def spa_path(path):
    """Compiles the HTML then returns it as a static file to allow for SPA paths to work."""
    return render_template("index.html")
