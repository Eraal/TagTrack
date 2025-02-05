from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
from extensions import db 
from models import Item, Category, Location
import os
from flask import send_from_directory
from werkzeug.utils import secure_filename

# Initialize the Flask app
app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/tagtrack'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'  # Folder to store uploaded images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed file extensions

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


db.init_app(app) 

from models import *

with app.app_context():
    db.create_all()  

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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
    
    total_items_lost = Item.query.filter(Item.status == 'lost', Item.date_reported >= start_date).count() 
    total_items_found = Item.query.filter_by(status='found').count() 

    print('Go to Dashboard')


    return render_template('dashboard.html',
                           total_items_active=total_items_active,
                           total_items_lost=total_items_lost,
                           total_items_found=total_items_found,
                           filter_type=filter_type)

@app.route('/categories')
def categories():
    categories = Category.query.all()
    print('Go to Categories')
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


@app.route('/items/listEntryItem')
def list_entry_item_page():
    categories = Category.query.all()
    locations = Location.query.all()  # Fetch locations
    return render_template('items/listEntryItem.html', categories=categories, locations=locations)

@app.route('/api/items', methods=["GET"])
def get_items():
    items = Item.query.all()
    items_list = []

    for item in items:
        items_list.append({
            "id": item.id,
            "category": item.category.name if item.category else "Unknown",  # Now safe ✅
            "description": item.description,
            "location": item.location.name if item.location else "Unknown",  # Now safe ✅
            "date_reported": item.date_reported.strftime("%Y-%m-%d"),
            "status": item.status,
            "rfid_tag": item.rfid_tag,
            "image_file": item.image_file if item.image_file else "default.jpg"
        })
    
    return jsonify(items_list)

# API Route for managing items
@app.route("/api/items", methods=["POST"])
def list_entry_item_api():
    try:
        category_id = request.form.get("category_id")
        location_id = request.form.get("location_id")
        description = request.form.get("description")
        date_reported = request.form.get("date_reported")
        status = request.form.get("status")
        rfid_tag = request.form.get("rfid_tag")
        image = request.files.get("image")

        # Debugging
        print(f"Received Data: {request.form}")

        # Ensure category_id and location_id are valid
        if not category_id or not location_id:
            return jsonify({"error": "Category and location are required!"}), 400

        category_id = int(category_id)
        location_id = int(location_id)

        if not Category.query.get(category_id):
            return jsonify({"error": "Invalid category ID"}), 400

        if not Location.query.get(location_id):
            return jsonify({"error": "Invalid location ID"}), 400

        # Ensure date format
        try:
            date_reported = datetime.strptime(date_reported, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

        # Handle image upload
        image_file = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            image_file = filename

        # Insert into database
        new_item = Item(
            category_id=category_id,
            description=description,
            location_id=location_id,
            date_reported=date_reported,
            image_file=image_file,
            status=status,
            rfid_tag=rfid_tag
        )

        db.session.add(new_item)
        db.session.commit()

        return jsonify({"message": "Item added successfully!"}), 201

    except ValueError:
        return jsonify({"error": "Invalid ID format. Ensure category_id and location_id are integers."}), 400
    except Exception as e:
        db.session.rollback()
        print("Error:", str(e))  # Debugging
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/locations', methods=["GET"])
def get_active_locations():
    """Fetch all locations"""
    locations = Location.query.all()
    return jsonify([{"id": loc.id, "name": loc.name} for loc in locations])

@app.route('/api/categories', methods=["GET"])
def get_active_categories():
    """Fetch all active categories"""
    categories = Category.query.filter_by(status='Active').all()
    print("Fetched categories:", categories)  # Debugging: Print fetched categories
    return jsonify([{"id": cat.id, "name": cat.name} for cat in categories])

if __name__ == '__main__':
    app.run(debug=True)