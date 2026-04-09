from app import create_app
from models import db, User, MenuItem, CartItem

app = create_app()

with app.app_context():
    user = User.query.filter_by(role='user').first()
        
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
            
        # Get cart item for this user
        cart_item = CartItem.query.filter_by(user_id=user.id).first()
        if not cart_item:
            print("No item in cart, adding one...")
            menu_item = MenuItem.query.first()
            cart_item = CartItem(user_id=user.id, menu_item_id=menu_item.id, quantity=1)
            db.session.add(cart_item)
            db.session.commit()
            
        print(f"Testing update_cart to 0 for cart_item {cart_item.id}")
        # Send AJAX request to decrease quantity to 0
        response = client.post(
            f'/user/update_cart/{cart_item.id}',
            data={'action': 'decrease'},
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        print("Status", response.status_code)
        
        try:
            print(response.get_json())
        except Exception as e:
            print("Error getting json:", e)
        print(response.get_data(as_text=True))
