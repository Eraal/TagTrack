from flask import Flask, render_template, request, jsonify, url_for, redirect, session, flash
from functools import wraps
from datetime import datetime, timedelta
from models import Item, Category, Location
import os
from flask import send_from_directory
from werkzeug.utils import secure_filename
from models import db, Item, Claim, Category, Location, User
from collections import defaultdict


# Initialize the Flask app
app = Flask(__name__)

app.secret_key = "Rald" 

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


########################################### ADMIN PAGE ####################################


ADMIN_CREDENTIALS = {"admin": "123"}

# ------------------ ADMIN LOGIN ROUTE ------------------
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))  # Redirect to dashboard
        else:
            flash("Invalid credentials!", "danger")

    return render_template('admin/admin_login.html')

# ------------------ ADMIN LOGOUT ROUTE ------------------
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash("Logged out successfully!", "info")
    return redirect(url_for('admin_login'))

# ------------------ ADMIN AUTH DECORATOR ------------------
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash("Please log in to access the dashboard!", "warning")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


############################################################## DASHBOARD ###################################################################

@app.route('/')
@admin_required
def dashboard():

    total_items_lost = Item.query.count()
    total_items_active = Item.query.filter_by(status='Unclaimed').count()  
    total_tagged_items = Item.query.filter(Item.rfid_tag != "None").count()  
    total_items_found = Item.query.filter_by(status='Claimed').count()
  

    lost_items_by_category = (
        db.session.query(Category.name, db.func.count(Item.id))
        .join(Item, Category.id == Item.category_id)
        .filter(Item.status == 'Unclaimed')  # Only count unclaimed lost items
        .group_by(Category.name)
        .all()
    )

    lost_items_by_category_dict = {category: count for category, count in lost_items_by_category}


    latest_tagged_items = (
        Item.query.filter(Item.rfid_tag == "Tagged", Item.status == "Unclaimed")
        .order_by(Item.date_reported.desc())  # Assuming date_reported is used for latest items
        .limit(5)
        .all()
    )
 
    print("Fetched latest tagged lost items:", latest_tagged_items)

    return render_template(
        'dashboard.html',
        total_items_active=total_items_active,
        total_tagged_items=total_tagged_items,
        total_items_lost=total_items_lost,
        total_items_found=total_items_found,
        lost_items_by_category=lost_items_by_category_dict,
        latest_tagged_items=latest_tagged_items
    )

@app.route('/found-items-by-location')
def found_items_by_location():
    results = (
        db.session.query(Location.name, db.func.count(Item.id))
        .join(Item, Location.id == Item.location_id)
        .filter(Item.status == 'Unclaimed')  # Only count found items
        .group_by(Location.name)
        .all()
    )

    data = [{"location": loc, "count": count} for loc, count in results]
    return jsonify(data)


############################################## UPDATE ITEM ON LIST ENTRY ##########################################

@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    try:
        item = Item.query.get(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404

        print(f"Current item status: {item.status}")

        if "category_id" in request.form and request.form["category_id"].isdigit():
            item.category_id = int(request.form["category_id"])

        if "location_id" in request.form and request.form["location_id"].isdigit():
            item.location_id = int(request.form["location_id"])

        if "description" in request.form:
            item.description = request.form["description"].strip()

        if "date_reported" in request.form:
            try:
                item.date_reported = datetime.strptime(request.form["date_reported"], "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

        if "status" in request.form:
            new_status = request.form["status"].strip()
            print(f"New status: {new_status}") 

            if item.status != "Claimed" and new_status == "Claimed":
                print("Status changed to Claimed. Creating a new claim record...") 
                item.status = "Claimed"

                claim_entry = Claim(item_id=item.id, claim_date=datetime.utcnow(), status="Claimed")
                db.session.add(claim_entry)
            else:
                item.status = new_status

        if "rfid_tag" in request.form:
            item.rfid_tag = request.form["rfid_tag"].strip()

        if "image" in request.files:
            image = request.files["image"]
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                item.image_file = filename 

        db.session.commit()
        return jsonify({"message": "Item updated successfully!"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error updating item: {str(e)}")  
        return jsonify({"error": str(e)}), 500
    

@app.route('/api/claimed-items', methods=['GET'])
def get_claimed_items():
    """Fetch all claimed items with their claim date."""
    claimed_items = (
        db.session.query(
            Item.id, Item.description, Item.status, Item.date_reported.label("date_reported"),
            Claim.claim_date.label("date_claimed"), Category.name.label("category"),
            Item.rfid_tag
        )
        .join(Claim, Claim.item_id == Item.id)
        .join(Category, Item.category_id == Category.id)
        .filter(Item.status == "Claimed") 
        .all()
    )

    result = []
    for item in claimed_items:
        result.append({
            "id": item.id,
            "category": item.category,
            "description": item.description,
            "date_reported": item.date_reported.strftime("%Y-%m-%d"),
            "date_claimed": item.date_claimed.strftime("%Y-%m-%d") if item.date_claimed else "Not Available",
            "rfid_tag": item.rfid_tag,
            "status": item.status
        })

    return jsonify(result)



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

@app.route("/get_categories", methods=["GET"])
def get_categories():
    categories = Category.query.all()
    categories_data = []

    for category in categories:
        has_items = db.session.query(Item.id).filter_by(category_id=category.id).first() is not None
        status = "Active" if has_items else "Inactive"

        categories_data.append({
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "status": status, 
        })

    return jsonify(categories_data)


@app.route('/update_category/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    try:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({"error": "Category not found"}), 404

        data = request.json
        category.name = data.get("name", category.name)
        category.description = data.get("description", category.description)
        category.status = data.get("status", category.status)

        db.session.commit()
        return jsonify({"message": "Category updated successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@app.route('/delete_category/<int:id>', methods=['DELETE'])
def delete_category(id):
    category = Category.query.get(id)
    if not category:
        return jsonify({"error": "Category not found"}), 404

    db.session.delete(category)
    db.session.commit()
    
    return jsonify({"message": "Category deleted successfully"}), 200


######################################## ITEMS/ LIST ENTRY ITEMS ####################################################

@app.route('/items/listEntryItem')
def list_entry_item_page():
    categories = Category.query.all()
    locations = Location.query.all() 
    return render_template('items/listEntryItem.html', categories=categories, locations=locations)

@app.route("/api/items", methods=["GET"])
def get_items():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    location_id = request.args.get("location", "").strip()
    date_sort = request.args.get("date", "").strip()  # Sorting order

    query = Item.query

    # Search by description (case-insensitive)
    if search:
        query = query.filter(Item.description.ilike(f"%{search}%"))

    # Filter by status (Claimed / Unclaimed)
    if status:
        query = query.filter(Item.status == status)

    # Filter by location_id (ensure conversion to integer)
    if location_id.isdigit():
        query = query.filter(Item.location_id == int(location_id))

    # Sort by date (Newest / Oldest)
    if date_sort.lower() == "newest":
        query = query.order_by(Item.date_reported.desc())
    elif date_sort.lower() == "oldest":
        query = query.order_by(Item.date_reported.asc())

    items = query.all()

    return jsonify([
        {
            "id": item.id,
            "category": item.category.name if item.category else "Unknown",
            "description": item.description,
            "location": item.location.name if item.location else "Unknown",
            "location_id": item.location_id,
            "date_reported": item.date_reported.strftime("%B %d, %Y"),
            "status": item.status,
            "rfid_tag": item.rfid_tag,
            "image_file": item.image_file if item.image_file else "default.jpg"
        }
        for item in items
    ])


@app.route("/api/items/<int:item_id>", methods=["GET"])
def get_item_by_id(item_id):
    item = Item.query.get(item_id)

    if not item:
        return jsonify({"error": "Item not found"}), 404

    return jsonify({
        "id": item.id,
        "category_id": item.category_id,
        "description": item.description,
        "location": item.location.name if item.location else "Unknown",
        "location_id": item.location_id,
        "date_reported": item.date_reported.strftime("%Y-%m-%d"),
        "status": item.status,
        "rfid_tag": item.rfid_tag,
        "image_file": item.image_file if item.image_file else "default.jpg"
    })

@app.route("/api/items", methods=["POST"])
def list_entry_item_api():
    try:
        # Get form data
        category_id = request.form.get("category_id")
        location_id = request.form.get("location_id")
        description = request.form.get("description")
        date_reported = request.form.get("date_reported")
        status = request.form.get("status")
        rfid_tag = request.form.get("rfid_tag")
        image = request.files.get("image")

        print(f"Received Data: {request.form}")

        # Validate required fields
        if not category_id or not location_id:
            return jsonify({"error": "Category and location are required!"}), 400

        # Convert IDs to integers
        category_id = int(category_id)
        location_id = int(location_id)

        # Validate category and location IDs
        if not Category.query.get(category_id):
            return jsonify({"error": "Invalid category ID"}), 400

        if not Location.query.get(location_id):
            return jsonify({"error": "Invalid location ID"}), 400

        # Parse date
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

        # Create new item
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


#################### LIST TAG ITEMS ####################################################

@app.route('/api/tagged-items', methods=['GET'])
def get_tagged_items():
    # Filter items where rfid_tag is not None and not an empty string
    items = Item.query.filter(
        Item.rfid_tag.isnot(None),  # Exclude NULL values
        Item.rfid_tag != "None"         # Exclude empty strings
    ).all()

    items_list = [
        {
            "id": item.id,
            "category": item.category.name,
            "description": item.description,
            "location": item.location.name,
            "date_reported": item.date_reported.strftime("%Y-%m-%d"),
            "status": item.status,
            "image_file": item.image_file,
            "rfid_tag": item.rfid_tag,
            "owner_name": item.owner.name if item.owner else "N/A",
            "owner_email": item.owner.email if item.owner else "N/A",
            "owner_student_id": item.owner.student_id if item.owner else "N/A",
            "owner_contact": item.owner.contact_number if item.owner else "N/A",
        }
        for item in items
    ]
    print(items_list)  # ✅ Debugging: Print the data in Flask console
    return jsonify(items_list)



@app.route('/listtagitems')
def listtagitems():
    return render_template('/items/listTagItem.html')


@app.route('/api/item/<int:item_id>')
def get_item_details(item_id):
    item = Item.query.get_or_404(item_id)
    
    # Find the latest claim (if any)
    claim = Claim.query.filter_by(item_id=item.id).first()
    owner = User.query.get(claim.user_id) if claim else None

    return jsonify({
        "id": item.id,
        "category": item.category.name,
        "description": item.description,
        "location": item.location.name,
        "date_reported": item.date_reported.strftime('%Y-%m-%d'),
        "status": item.status,
        "image_file": item.image_file,
        "owner_name": owner.name if owner else "Unclaimed",
        "owner_email": owner.email if owner else "N/A"
    })

# routes.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from extensions import db
from models import Item, Category, Location, User, Claim

# Create a blueprint for tagged items functionality
tagged_items_bp = Blueprint('tagged_items', __name__)

# Render the tagged items page
@tagged_items_bp.route('/tagged-items')
def tagged_items_page():
    return render_template('tagged_items.html')

# API routes for frontend AJAX calls
@tagged_items_bp.route('/api/tagged-items', methods=['GET'])
def get_tagged_items():
    # Query items with RFID tags
    items_query = db.session.query(
        Item.id,
        Item.description,
        Item.date_reported,
        Item.image_file,
        Item.rfid_tag,
        Item.status,
        Item.category_id,
        Item.location_id,
        Item.owner_id,
        Category.name.label('category'),
        Location.name.label('location'),
        User.name.label('owner_name'),
        User.email.label('owner_email'),
        User.student_id.label('owner_student_id'),
        User.contact_number.label('owner_contact')
    ).join(
        Category, Item.category_id == Category.id
    ).join(
        Location, Item.location_id == Location.id
    ).outerjoin(
        User, Item.owner_id == User.id
    ).filter(
        Item.rfid_tag.isnot(None),
        Item.rfid_tag != ''
    ).all()
    
    # Convert to list of dictionaries
    items = []
    for item in items_query:
        item_dict = {
            'id': item.id,
            'description': item.description,
            'date_reported': item.date_reported.strftime('%Y-%m-%d'),
            'image_file': item.image_file,
            'rfid_tag': item.rfid_tag,
            'status': item.status,
            'category_id': item.category_id,
            'location_id': item.location_id,
            'owner_id': item.owner_id,
            'category': item.category,
            'location': item.location,
            'owner_name': item.owner_name,
            'owner_email': item.owner_email,
            'owner_student_id': item.owner_student_id,
            'owner_contact': item.owner_contact
        }
        items.append(item_dict)
    
    return jsonify(items)







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

############################################################ USER ################################################

@app.route('/users/landingpage')
def landingpage():
    return render_template('users/landingpage.html')

@app.route('/users/lostandfounditem')
def lostandfound():
    # Get filter parameters
    category_id = request.args.get('category', type=int)
    location_id = request.args.get('location', type=int)
    status = request.args.get('status')
    date_filter = request.args.get('date')
    search = request.args.get('search')
    has_rfid = request.args.get('has_rfid')
    
    # Base query
    query = Item.query
    
    # Apply filters
    if category_id:
        query = query.filter(Item.category_id == category_id)
    
    if location_id:
        query = query.filter(Item.location_id == location_id)
    
    if status:
        query = query.filter(Item.status == status)
    
    if search:
        query = query.filter(Item.description.ilike(f'%{search}%'))
    
    # Filter by RFID tag presence
    if has_rfid == 'yes':
        query = query.filter(Item.rfid_tag.isnot(None))
        query = query.filter(Item.rfid_tag != '')
    
    # Date filter
    today = datetime.now().date()
    if date_filter == 'today':
        query = query.filter(Item.date_reported == today)
    elif date_filter == 'week':
        # Calculate the date 7 days ago
        week_ago = today - timedelta(days=7)
        query = query.filter(Item.date_reported >= week_ago)
    elif date_filter == 'month':
        # Calculate the date 30 days ago
        month_ago = today - timedelta(days=30)
        query = query.filter(Item.date_reported >= month_ago)
    
    # Execute query to get the filtered items
    items = query.order_by(Item.date_reported.desc()).all()
    
    # Print debug information
    print(f"Query returned {len(items)} items")
    
    # Get all categories and locations for filters
    categories = Category.query.filter_by(status="Active").all()
    locations = Location.query.all()
    
    return render_template(
        'users/lostandfounditem.html', 
        items=items,
        categories=categories,
        locations=locations
    )



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)