from flask import Flask, render_template, request
from datetime import datetime, timedelta
from extensions import db 
from models import Item

# Initialize the Flask app
app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/tagtrack'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with app configuration
db.init_app(app)  # Bind db to the app

# Import models after initializing db
from models import *

# Ensure that tables are created inside the application context
with app.app_context():
    db.create_all()  

@app.route('/')
def dashboard():
    # Get the filter type from the query parameters (default to 'today')
    filter_type = request.args.get('filter', 'today')

    # Calculate the date range based on the filter
    today = datetime.today()
    if filter_type == 'today':
        start_date = today
    elif filter_type == 'week':
        start_date = today - timedelta(days=today.weekday())  # Start of the current week
    elif filter_type == 'month':
        start_date = today.replace(day=1)  # Start of the current month
    elif filter_type == 'year':
        start_date = today.replace(month=1, day=1)  # Start of the current year

    # Query the database to get the required counts
    total_items_active = Item.query.filter_by(status='active').count()  # Count active items
    total_tagged_items = Item.query.filter_by(is_tagged=True).count()  # Count tagged items
    total_items_lost = Item.query.filter(Item.status == 'lost', Item.date_reported >= start_date).count()  # Count lost items with filter
    total_items_found = Item.query.filter_by(status='found').count()  # Count found items

    # Pass the counts and filter type to the template
    return render_template('dashboard.html',
                           total_items_active=total_items_active,
                           total_tagged_items=total_tagged_items,
                           total_items_lost=total_items_lost,
                           total_items_found=total_items_found,
                           filter_type=filter_type)

if __name__ == '__main__':
    app.run(debug=True)
