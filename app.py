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

####################################### DASHBOARD ####################################################

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

    total_items_lost = Item.query.count()
    total_items_active = Item.query.filter_by(status='Unclaimed').count()  
    total_tagged_items = Item.query.filter(Item.rfid_tag.isnot(None)).count()  
    total_items_found = Item.query.filter_by(status='Claimed').count()

    print('Go to Dashboard')

    return render_template(
        'dashboard.html',
        total_items_active=total_items_active,
        total_tagged_items=total_tagged_items,
        total_items_lost=total_items_lost, 
        total_items_found=total_items_found,
        filter_type=filter_type
    )



################################# CATEGORIES ####################################################

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


######################################## ITEMS/ LIST ENTRY ITEMS ####################################################

@app.route('/items/listEntryItem')
def list_entry_item_page():
    categories = Category.query.all()
    locations = Location.query.all() 
    return render_template('items/listEntryItem.html', categories=categories, locations=locations)

@app.route('/api/items', methods=["GET"])
def get_items():
    """
    This function now serves both `/api/items` and `/get_items`
    If there are filter parameters, it filters results (previously handled by `/get_items`).
    """
    search = request.args.get("search", "")
    status = request.args.get("status", "")
    location = request.args.get("location", "")
    date = request.args.get("date", "")

    query = Item.query

    if search:
        query = query.filter(Item.description.ilike(f"%{search}%"))
    if status:
        query = query.filter(Item.status == status)
    if location:
        query = query.filter(Item.location_id == Location.id, Location.name == location)
    if date:
        query = query.order_by(Item.date_reported.desc() if date == "Newest" else Item.date_reported.asc())

    items = query.all()

    return jsonify([
        {
            "id": item.id,
            "category": item.category.name if item.category else "Unknown",
            "description": item.description,
            "location": item.location.name if item.location else "Unknown",
            "date_reported": item.date_reported.strftime("%B %d, %Y"),
            "status": item.status,
            "rfid_tag": item.rfid_tag,
            "image_file": item.image_file if item.image_file else "default.jpg"
        } for item in items
    ])

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

        print(f"Received Data: {request.form}")

        if not category_id or not location_id:
            return jsonify({"error": "Category and location are required!"}), 400

        category_id = int(category_id)
        location_id = int(location_id)

        if not Category.query.get(category_id):
            return jsonify({"error": "Invalid category ID"}), 400

        if not Location.query.get(location_id):
            return jsonify({"error": "Invalid location ID"}), 400

        try:
            date_reported = datetime.strptime(date_reported, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

        image_file = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            image_file = filename

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
        print("Error:", str(e)) 
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


#################### LIST ####################################################

@app.route('/listtagitems')
def listtagitems():
    return render_template('/items/listTagItem.html')

#################### TOTAL LOST ITEM ####################################################


@app.route('/items/totalLostItem')
def total_lost_items():
    
    status_filter = request.args.get("status", "")
    category_filter = request.args.get("category", "")
    tag_filter = request.args.get("tag", "")

    query = (
        db.session.query(
            Item.id, Item.description, Item.status, Item.date_reported.label("date_reported"),
            Claim.claim_date.label("date_claimed"), Category.name.label("category"),
            Item.rfid_tag
        )
        .outerjoin(Claim, Claim.item_id == Item.id)  
        .join(Category, Item.category_id == Category.id) 
    )

    if status_filter in ["Claimed", "Unclaimed"]:
        query = query.filter(Item.status == status_filter)

    if category_filter:
        query = query.filter(Category.name == category_filter)

    if tag_filter == "Tagged":
        query = query.filter(Item.rfid_tag.isnot(None)) 
    elif tag_filter == "Not Tagged":
        query = query.filter(Item.rfid_tag.is_(None)) 

    lost_items = query.all()

    categories = Category.query.with_entities(Category.name).distinct().all()
    categories = [cat.name for cat in categories]

    return render_template(
        "items/totalLostItem.html",
        lost_items=lost_items,
        total_lost_items_count=len(lost_items),
        categories=categories
    )

####### TOTAL LOST ITEMMM ####################################################

@app.route('/items/totalFoundItem')
def total_found_items():
  
    category_filter = request.args.get("category", "")
    tag_filter = request.args.get("tag", "")

    query = (
        db.session.query(
            Item.id, Item.description, Item.status, Item.date_reported.label("date_found"),
            Claim.claim_date.label("date_claimed"), Category.name.label("category"),
            Item.rfid_tag
        )
        .outerjoin(Claim, Claim.item_id == Item.id)
        .join(Category, Item.category_id == Category.id) 
        .filter(Item.status == "Claimed")  
    )

    if category_filter:
        query = query.filter(Category.name == category_filter)

    if tag_filter == "Tagged":
        query = query.filter(Item.rfid_tag.isnot(None))
    elif tag_filter == "Not Tagged":
        query = query.filter(Item.rfid_tag.is_(None)) 

    found_items = query.all()

    categories = Category.query.with_entities(Category.name).distinct().all()
    categories = [cat.name for cat in categories]

    return render_template(
        "items/totalFoundItem.html",
        found_items=found_items,
        total_found_items_count=len(found_items),
        categories=categories
    )



if __name__ == '__main__':
    app.run(debug=True)