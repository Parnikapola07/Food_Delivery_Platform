from app import create_app
from models import db, User, MenuItem, CartItem

app = create_app()

with app.app_context():
    user = User.query.filter_by(role='user').first()
    if not user:
        print("No user found")
        
    menu_items = MenuItem.query.all()
    if not menu_items:
        print("No menu item")
        
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
            
        print("Clearing cart for user")
        CartItem.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        
        # Test 1: Add new item to empty cart
        print(f"\n--- Testing add_to_cart empty cart, item {menu_items[0].id} ---")
        try:
            response = client.post(
                f'/user/add_to_cart/{menu_items[0].id}',
                headers={'X-Requested-With': 'XMLHttpRequest'}
            )
            print("Status:", response.status_code)
            print("Is JSON:", response.is_json)
            print("Data:", response.get_data(as_text=True))
        except Exception as e:
            print("EXCEPTION:", e)

        # Test 2: Add same item again
        print(f"\n--- Testing add_to_cart same item {menu_items[0].id} ---")
        try:
            response = client.post(
                f'/user/add_to_cart/{menu_items[0].id}',
                headers={'X-Requested-With': 'XMLHttpRequest'}
            )
            print("Status:", response.status_code)
            print("Is JSON:", response.is_json)
            print("Data:", response.get_data(as_text=True))
        except Exception as e:
            print("EXCEPTION:", e)
