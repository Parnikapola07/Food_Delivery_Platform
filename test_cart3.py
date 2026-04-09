from app import create_app
from models import db, User, MenuItem, CartItem

app = create_app()

with app.app_context():
    user = User.query.filter_by(role='user').first()
        
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
            
        print("Clearing cart")
        CartItem.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        
        menu_item = MenuItem.query.first()
        cart_item = CartItem(user_id=user.id, menu_item_id=menu_item.id, quantity=1)
        db.session.add(cart_item)
        db.session.commit()
            
        print(f"Testing update_cart decrease to 0 for cart_item {cart_item.id}")
        response = client.post(
            f'/user/update_cart/{cart_item.id}',
            data={'action': 'decrease'},
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        print("Status", response.status_code)
        print("Data", response.get_data(as_text=True))
