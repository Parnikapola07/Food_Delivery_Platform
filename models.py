from extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user') # 'user', 'restaurant', 'delivery'
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    
    # Relationships
    menus = db.relationship('MenuItem', backref='restaurant', lazy=True, foreign_keys='MenuItem.restaurant_id')
    orders = db.relationship('Order', backref='customer', lazy=True, foreign_keys='Order.user_id')
    restaurant_orders = db.relationship('Order', backref='restaurant', lazy=True, foreign_keys='Order.restaurant_id')
    delivery_assignments = db.relationship('Order', backref='delivery_partner', lazy=True, foreign_keys='Order.delivery_partner_id')
    cart_items = db.relationship('CartItem', backref='user', lazy=True)

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(200), nullable=True, default='default_food.jpg')
    restaurant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    
    menu_item = db.relationship('MenuItem')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    delivery_partner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    status = db.Column(db.String(50), nullable=False, default='Pending') 
    # Statuses: Pending, Accepted, Preparing, Ready, Out for Delivery, Delivered
    total_amount = db.Column(db.Float, nullable=False)
    delivery_fee = db.Column(db.Float, nullable=False, default=5.0)
    platform_fee = db.Column(db.Float, nullable=False, default=2.0)
    delivery_address = db.Column(db.Text, nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    restaurant_instructions = db.Column(db.Text, nullable=True)
    delivery_instructions = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_time = db.Column(db.Float, nullable=False)
    
    menu_item = db.relationship('MenuItem')

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    order = db.relationship('Order', backref='review')
    user = db.relationship('User', foreign_keys=[user_id])
