from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import MenuItem, Order
from extensions import db

restaurant_bp = Blueprint('restaurant', __name__)

@restaurant_bp.before_request
def check_role():
    if current_user.is_authenticated and current_user.role != 'restaurant':
        flash('Please login as a restaurant.', 'warning')
        return redirect(url_for('auth.login', role='restaurant'))

@restaurant_bp.route('/dashboard')
@login_required
def dashboard():
    total_orders = Order.query.filter_by(restaurant_id=current_user.id).count()
    
    # Calculate revenue based on subtotal (total - fees)
    completed_orders = Order.query.filter_by(restaurant_id=current_user.id, status='Delivered').all()
    revenue = sum(order.total_amount - order.delivery_fee - order.platform_fee for order in completed_orders)
    
    recent_orders = Order.query.filter_by(restaurant_id=current_user.id).order_by(Order.created_at.desc()).limit(5).all()
    
    return render_template('restaurant/dashboard.html', total_orders=total_orders, revenue=revenue, recent_orders=recent_orders)

@restaurant_bp.route('/menu/add', methods=['GET', 'POST'])
@login_required
def add_menu():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        category = request.form.get('category')
        image_url = request.form.get('image_url') or 'default_food.jpg'
        
        new_item = MenuItem(
            name=name,
            description=description,
            price=price,
            category=category,
            image_url=image_url,
            restaurant_id=current_user.id
        )
        db.session.add(new_item)
        db.session.commit()
        flash('Menu item added successfully!', 'success')
        return redirect(url_for('restaurant.manage_menu'))
        
    return render_template('restaurant/add_menu.html')

@restaurant_bp.route('/menu/manage')
@login_required
def manage_menu():
    menu_items = MenuItem.query.filter_by(restaurant_id=current_user.id).all()
    return render_template('restaurant/manage_menu.html', menu_items=menu_items)

@restaurant_bp.route('/menu/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_menu(item_id):
    item = MenuItem.query.get_or_404(item_id)
    if item.restaurant_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
        flash('Menu item deleted.', 'success')
    return redirect(url_for('restaurant.manage_menu'))

@restaurant_bp.route('/menu/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_menu(item_id):
    item = MenuItem.query.get_or_404(item_id)
    
    # Ensure the user owns this menu item
    if item.restaurant_id != current_user.id:
        flash('Unauthorized to edit this item.', 'danger')
        return redirect(url_for('restaurant.manage_menu'))
        
    if request.method == 'POST':
        item.name = request.form.get('name')
        item.description = request.form.get('description')
        item.price = float(request.form.get('price'))
        item.category = request.form.get('category')
        item.image_url = request.form.get('image_url') or 'default_food.jpg'
        
        db.session.commit()
        flash('Menu item updated successfully!', 'success')
        return redirect(url_for('restaurant.manage_menu'))
        
    return render_template('restaurant/edit_menu.html', item=item)

@restaurant_bp.route('/menu/toggle_status/<int:item_id>', methods=['POST'])
@login_required
def toggle_menu_status(item_id):
    item = MenuItem.query.get_or_404(item_id)
    if item.restaurant_id == current_user.id:
        item.is_active = not item.is_active
        db.session.commit()
        status = "available" if item.is_active else "unavailable"
        flash(f'Menu item marked as {status}.', 'success')
    return redirect(url_for('restaurant.manage_menu'))

@restaurant_bp.route('/orders')
@login_required
def orders():
    all_orders = Order.query.filter_by(restaurant_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('restaurant/orders.html', orders=all_orders)

@restaurant_bp.route('/orders/update/<int:order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    if order.restaurant_id == current_user.id:
        new_status = request.form.get('status')
        # Restaurant handles states: Pending -> Accepted -> Preparing -> Ready
        if new_status in ['Accepted', 'Preparing', 'Ready', 'Rejected']:
            order.status = new_status
            db.session.commit()
            flash(f'Order status updated to {new_status}.', 'success')
    return redirect(url_for('restaurant.orders'))
