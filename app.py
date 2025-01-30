from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
from extensions import db 
from models import Item

# Initialize the Flask app
app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/tagtrack'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app) 

from models import *

with app.app_context():
    db.create_all()  

@app.route('/')
def dashboard():
    filter_type = request.args.get('filter', 'today')

    today = datetime.today()
    if filter_type == 'today':
        start_date = today
    elif filter_type == 'week':
        start_date = today - timedelta(days=today.weekday())  
    elif filter_type == 'month':
        start_date = today.replace(day=1)  
    elif filter_type == 'year':
        start_date = today.replace(month=1, day=1) 

    total_items_active = Item.query.filter_by(status='active').count() 
    total_tagged_items = Item.query.filter_by(is_tagged=True).count()  
    total_items_lost = Item.query.filter(Item.status == 'lost', Item.date_reported >= start_date).count() 
    total_items_found = Item.query.filter_by(status='found').count() 


    return render_template('dashboard.html',
                           total_items_active=total_items_active,
                           total_tagged_items=total_tagged_items,
                           total_items_lost=total_items_lost,
                           total_items_found=total_items_found,
                           filter_type=filter_type)

@app.route('/categories')
def categories():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@app.route('/add_category', methods=['POST'])
def add_category():
    data = request.json
    new_category = Category(name=data['name'], description=data['description'])
    db.session.add(new_category)
    db.session.commit()
    return jsonify({"message": "Category added successfully!"}), 201

@app.route('/get_categories')
def get_categories():
    categories = Category.query.all()
    return jsonify([{"id": cat.id, "name": cat.name, "description": cat.description, "status": cat.status} for cat in categories])

if __name__ == '__main__':
    app.run(debug=True)