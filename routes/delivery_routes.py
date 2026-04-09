from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Order
from extensions import db

delivery_bp = Blueprint('delivery', __name__)

@delivery_bp.before_request
def check_role():
    if current_user.is_authenticated and current_user.role != 'delivery':
        flash('Please login as a delivery partner.', 'warning')
        return redirect(url_for('auth.login', role='delivery'))

from datetime import datetime

@delivery_bp.route('/dashboard')
@login_required
def dashboard():
    # Calculate today's earnings and deliveries
    today = datetime.utcnow().date()
    today_orders = Order.query.filter(
        Order.delivery_partner_id == current_user.id,
        Order.status == 'Delivered'
    ).all()
    
    # Filter for orders completed today
    today_orders = [o for o in today_orders if o.created_at.date() == today]
    today_earnings = sum(o.delivery_fee for o in today_orders)
    
    # Show orders that are 'Ready' and not yet assigned
    available_orders = Order.query.filter_by(status='Ready', delivery_partner_id=None).order_by(Order.created_at.desc()).all()
    
    return render_template('delivery/dashboard.html', 
                           available_orders=available_orders,
                           today_deliveries=len(today_orders),
                           today_earnings=today_earnings)

@delivery_bp.route('/assigned-orders')
@login_required
def assigned_orders():
    orders = Order.query.filter_by(delivery_partner_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('delivery/assigned_orders.html', orders=orders)

@delivery_bp.route('/accept-order/<int:order_id>', methods=['POST'])
@login_required
def accept_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status == 'Ready' and order.delivery_partner_id is None:
        order.delivery_partner_id = current_user.id
        order.status = 'Out for Delivery' # As soon as accepted, they pick it up
        db.session.commit()
        flash('Order accepted. It is now out for delivery.', 'success')
    else:
        flash('Order is no longer available.', 'danger')
    return redirect(url_for('delivery.assigned_orders'))

@delivery_bp.route('/update-status/<int:order_id>', methods=['POST'])
@login_required
def update_status(order_id):
    order = Order.query.get_or_404(order_id)
    if order.delivery_partner_id == current_user.id:
        status = request.form.get('status')
        if status in ['Out for Delivery', 'Delivered']:
            order.status = status
            db.session.commit()
            flash(f'Order marked as {status}.', 'success')
    return redirect(url_for('delivery.assigned_orders'))
