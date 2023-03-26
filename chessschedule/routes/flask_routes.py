from ..app import app
from flask import send_from_directory

# Path for our main Svelte page
@app.route("/<path:path>")
def spa(path):
    # for js and css
    if path.startswith('assets'):
        return send_from_directory('../client/dist', path)
    # for images and other static files
    if "static" in path:
        return app.send_static_file('/'.join(path.split("/")[2:]))
    return send_from_directory('../client/dist', 'index.html')



    
@app.route('/')
def base():
    return send_from_directory('../client/dist', 'index.html')