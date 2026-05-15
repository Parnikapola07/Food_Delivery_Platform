from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import User, MenuItem, CartItem, Order, OrderItem, Review
from extensions import db
from sqlalchemy import or_

user_bp = Blueprint('user', __name__)

@user_bp.before_request
def check_role():
    if current_user.is_authenticated and current_user.role != 'user':
        # Flash a message or redirect to their portal instead of role_select
        flash('Redirecting to your portal.', 'info')
        return redirect(url_for(f'{current_user.role}.dashboard'))

@user_bp.route('/')
def home():
    restaurants = User.query.filter_by(role='restaurant').all()
    return render_template('user/home.html', restaurants=restaurants)

@user_bp.route('/api/search')
def api_search():
    search = request.args.get('q', '').strip()
    
    if not search:
        return {'restaurants': [], 'menu_items': [], 'grouped_results': []}

    # 1. Search for matching menu items
    menu_items = MenuItem.query.filter(
        MenuItem.is_active == True,
        or_(
            MenuItem.name.ilike(f'%{search}%'),
            MenuItem.description.ilike(f'%{search}%'),
            MenuItem.category.ilike(f'%{search}%')
        )
    ).all()
    
    # Group items by restaurant
    grouped_data = {}
    for item in menu_items:
        r_id = item.restaurant_id
        if r_id not in grouped_data:
            restaurant = User.query.get(r_id)
            if restaurant:
                grouped_data[r_id] = {
                    'restaurant_id': restaurant.id,
                    'restaurant_name': restaurant.username,
                    'restaurant_address': restaurant.address,
                    'restaurant_description': 'Top rated • Gourmet & Fast Food • 4.5 ★',
                    'items': []
                }
        
        if r_id in grouped_data:
            grouped_data[r_id]['items'].append({
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'price': float(item.price),
                'image_url': item.image_url or 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&q=80&w=400'
            })

    # 2. Search for matching restaurants (by name/address)
    restaurants = User.query.filter(
        User.role == 'restaurant',
        or_(User.username.ilike(f'%{search}%'), User.address.ilike(f'%{search}%'))
    ).all()
    
    restaurant_results = []
    for r in restaurants:
        restaurant_results.append({
            'id': r.id,
            'name': r.username,
            'address': r.address,
            'image_url': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&q=80&w=600'
        })
        
    # 3. Get user's cart if authenticated
    user_cart = {}
    if current_user.is_authenticated:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        for ci in cart_items:
            user_cart[ci.menu_item_id] = ci.quantity

    return {
        'restaurants': restaurant_results,
        'grouped_results': list(grouped_data.values()),
        'user_cart': user_cart
    }

@user_bp.route('/menu/<int:restaurant_id>')
def restaurant_detail(restaurant_id):
    restaurant = User.query.get_or_404(restaurant_id)
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
    
    # Check if there are items from another restaurant in cart
    cart_restaurant_id = None
    cart_quantities = {}
    cart_item_ids = {}
    if current_user.is_authenticated:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        if cart_items:
            cart_restaurant_id = cart_items[0].menu_item.restaurant_id
            for item in cart_items:
                cart_quantities[item.menu_item_id] = item.quantity
                cart_item_ids[item.menu_item_id] = item.id
            
    # Fetch reviews for this restaurant
    reviews = Review.query.filter_by(restaurant_id=restaurant_id).order_by(Review.created_at.desc()).all()
        
    return render_template('user/restaurant_detail.html', restaurant=restaurant, menu_items=menu_items, cart_restaurant_id=cart_restaurant_id, cart_quantities=cart_quantities, cart_item_ids=cart_item_ids, reviews=reviews)

@user_bp.route('/add_to_cart/<int:menu_item_id>', methods=['POST'])
@login_required
def add_to_cart(menu_item_id):
    action = request.args.get('action', 'increase')
    menu_item = MenuItem.query.get_or_404(menu_item_id)
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    # Prevent adding from multiple restaurants
    if cart_items and cart_items[0].menu_item.restaurant_id != menu_item.restaurant_id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'success': False, 'message': 'You can only order from one restaurant at a time. Clear cart to change restaurant.'}
        flash('You can only order from one restaurant at a time. Clear cart to change restaurant.', 'warning')
        return redirect(url_for('user.restaurant_detail', restaurant_id=menu_item.restaurant_id))
    
    existing_item = CartItem.query.filter_by(user_id=current_user.id, menu_item_id=menu_item_id).first()
    
    new_qty = 0
    if existing_item:
        if action == 'increase':
            existing_item.quantity += 1
        else:
            existing_item.quantity -= 1
            if existing_item.quantity <= 0:
                db.session.delete(existing_item)
                existing_item = None
        if existing_item: new_qty = existing_item.quantity
    elif action == 'increase':
        new_cart_item = CartItem()
        new_cart_item.user_id = current_user.id
        new_cart_item.menu_item_id = menu_item_id
        new_cart_item.quantity = 1
        db.session.add(new_cart_item)
        new_qty = 1
        
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_count = sum(item.quantity for item in CartItem.query.filter_by(user_id=current_user.id).all())
        return {
            'success': True, 
            'message': 'Cart updated.', 
            'cart_count': cart_count,
            'item_id': menu_item_id,
            'new_qty': new_qty
        }
        
    flash('Cart updated.', 'success')
    return redirect(url_for('user.restaurant_detail', restaurant_id=menu_item.restaurant_id))

@user_bp.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    subtotal = sum(item.menu_item.price * item.quantity for item in cart_items)
    delivery_fee = 5.0 if subtotal > 0 else 0
    platform_fee = 2.0 if subtotal > 0 else 0
    total = subtotal + delivery_fee + platform_fee
    return render_template('user/cart.html', cart_items=cart_items, subtotal=subtotal, delivery_fee=delivery_fee, platform_fee=platform_fee, total=total)

@user_bp.route('/update_cart/<int:cart_item_id>', methods=['POST'])
@login_required
def update_cart(cart_item_id):
    cart_item = CartItem.query.get_or_404(cart_item_id)
    if cart_item.user_id != current_user.id:
        return redirect(url_for('user.cart'))
        
    action = request.form.get('action')
    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease':
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            db.session.delete(cart_item)
    elif action == 'remove':
        db.session.delete(cart_item)
        cart_item.quantity = 0
            
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return updated totals and quantity
        all_items = CartItem.query.filter_by(user_id=current_user.id).all()
        subtotal = sum(item.menu_item.price * item.quantity for item in all_items)
        delivery_fee = 5.0 if subtotal > 0 else 0
        platform_fee = 2.0 if subtotal > 0 else 0
        total = subtotal + delivery_fee + platform_fee
        new_quantity = cart_item.quantity if cart_item.quantity > 0 else 0
        return {
            'success': True, 
            'item_total': cart_item.quantity * cart_item.menu_item.price if cart_item.quantity > 0 else 0,
            'quantity': new_quantity,
            'subtotal': subtotal,
            'delivery_fee': delivery_fee,
            'platform_fee': platform_fee,
            'total': total
        }
    
    return redirect(request.referrer or url_for('user.cart'))

@user_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('user.home'))
        
    subtotal = sum(item.menu_item.price * item.quantity for item in cart_items)
    delivery_fee = 5.0
    platform_fee = 2.0
    total = subtotal + delivery_fee + platform_fee
    
    if request.method == 'POST':
        address = request.form.get('address')
        phone = request.form.get('phone')
        restaurant_note = request.form.get('restaurant_instructions')
        delivery_note = request.form.get('delivery_instructions')
        
        restaurant_id = cart_items[0].menu_item.restaurant_id
        
        new_order = Order()
        new_order.user_id = current_user.id
        new_order.restaurant_id = restaurant_id
        new_order.total_amount = total
        new_order.delivery_fee = delivery_fee
        new_order.platform_fee = platform_fee
        new_order.delivery_address = address
        new_order.contact_phone = phone
        new_order.restaurant_instructions = restaurant_note
        new_order.delivery_instructions = delivery_note
        new_order.status = 'Pending'
        db.session.add(new_order)
        db.session.flush() # get order id
        
        for item in cart_items:
            order_item = OrderItem()
            order_item.order_id = new_order.id
            order_item.menu_item_id = item.menu_item_id
            order_item.quantity = item.quantity
            order_item.price_at_time = item.menu_item.price
            db.session.add(order_item)
            db.session.delete(item)
            
        db.session.commit()
        flash('Order placed successfully!', 'success')
        return redirect(url_for('user.order_tracking', order_id=new_order.id))
        
    return render_template('user/checkout.html', cart_items=cart_items, subtotal=subtotal, delivery_fee=delivery_fee, platform_fee=platform_fee, total=total)

@user_bp.route('/orders')
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('user/order_history.html', orders=orders)

@user_bp.route('/order-tracking/<int:order_id>')
@login_required
def order_tracking(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('user.home'))
    return render_template('user/order_tracking.html', order=order)

@user_bp.route('/api/order/status/<int:order_id>')
@login_required
def api_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        return {'error': 'Unauthorized'}, 403
    return {
        'status': order.status,
        'id': order.id
    }

@user_bp.route('/submit_review/<int:order_id>', methods=['POST'])
@login_required
def submit_review(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('user.order_history'))
        
    if order.status != 'Delivered':
        flash('You can only review delivered orders.', 'warning')
        return redirect(url_for('user.order_history'))
        
    if order.review:
        flash('You have already reviewed this order.', 'info')
        return redirect(url_for('user.order_history'))
        
    rating = int(request.form.get('rating'))
    comment = request.form.get('comment')
    
    new_review = Review()
    new_review.order_id = order.id
    new_review.user_id = current_user.id
    new_review.restaurant_id = order.restaurant_id
    new_review.rating = rating
    new_review.comment = comment
    
    db.session.add(new_review)
    db.session.commit()
    flash('Thank you for your review!', 'success')
    
    return redirect(url_for('user.order_history'))
