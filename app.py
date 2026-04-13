# to run the server: 
# python app.py

from flask import Flask, request
from flask import render_template
from werkzeug.middleware.proxy_fix import ProxyFix
import logging

app = Flask(__name__)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=2)

# 2. Configure the logger (Optional: customize the format)
logging.basicConfig(level=logging.INFO)

@app.before_request
def log_request_info():
    # This will run before every single request
    # Since we used ProxyFix, request.remote_addr is the REAL visitor IP
    app.logger.info('--- Incoming Request ---')
    app.logger.info(f"Real IP: {request.remote_addr}")
    app.logger.info(f"Path: {request.path}")
    app.logger.info(f"User Agent: {request.headers.get('User-Agent')}")


@app.route("/")
def index():
    return render_template(
            'index.html'
            )





if __name__ == '__main__': 
    app.run(debug=True, host="0.0.0.0", port=5000)
