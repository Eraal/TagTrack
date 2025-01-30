from extensions import db  # Import db from extensions.py

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))  # Added description field
    status = db.Column(db.String(20), default="Active")  # Added status field


# Locations Table
class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


# Items Table
class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id', ondelete='CASCADE'), nullable=False)
    date_reported = db.Column(db.Date, nullable=False)
    image_file = db.Column(db.String(255))
    rfid_tag = db.Column(db.String(255))
    is_tagged = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(50), nullable=False)


# Users Table
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=False)


# Claims Table
class Claim(db.Model):
    __tablename__ = 'claims'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    claim_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), nullable=False)