# to run the server: 
# python app.py

from flask import Flask, request, url_for, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from collections import defaultdict
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=2)

# 2. Configure the logger (Optional: customize the format)
logging.basicConfig(level=logging.INFO)

@app.before_request
def log_request_info():
    # This will run before every single request
    # Since we used ProxyFix, request.remote_addr is the REAL visitor IP
    app.logger.info('--- Incoming Request ---')
    app.logger.info(f"Date and Time (HKT): {datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')}")
    app.logger.info(f"Real IP: {request.remote_addr}")
    app.logger.info(f"Path: {request.path}")
    app.logger.info(f"User Agent: {request.headers.get('User-Agent')}")


# Database Setup (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vacation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route("/")
def index():
    return render_template(
            'index.html'
            )


# Database Models
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class Point(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    friend_name = db.Column(db.String(50), nullable=False)
    category_name = db.Column(db.String(50), nullable=False)
    day = db.Column(db.String(20), nullable=False)

# Create the database and default categories
with app.app_context():
    db.create_all()
    if not Category.query.first():
        db.session.commit()

# --- Routes ---
@app.route('/pointz')
def pointz():
    categories = Category.query.all()
    people = Person.query.order_by(Person.name).all()
    all_points = Point.query.all()
    
    summary = defaultdict(lambda: defaultdict(int))
    for p in all_points:
        summary[p.friend_name][p.category_name] += 1
        
    return render_template('pointz.html', categories=categories, people=people, summary=summary)

@app.route('/add_point', methods=['POST'])
def add_point():
    friend = request.form.get('friend_name')
    category = request.form.get('category_name')
    day = request.form.get('day')
    
    if friend and category:
        db.session.add(Point(friend_name=friend, category_name=category, day=day))
        db.session.commit()
    return redirect(url_for('pointz'))

@app.route('/add_category', methods=['POST'])
def add_category():
    name = request.form.get('cat_name').strip()
    if name and not Category.query.filter_by(name=name).first():
        db.session.add(Category(name=name))
        db.session.commit()
    return redirect(url_for('pointz'))

@app.route('/add_person', methods=['POST'])
def add_person():
    name = request.form.get('person_name').strip()
    if name and not Person.query.filter_by(name=name).first():
        db.session.add(Person(name=name))
        db.session.commit()
    return redirect(url_for('pointz'))


if __name__ == '__main__': 
    app.run(debug=True, host="0.0.0.0", port=5000)
