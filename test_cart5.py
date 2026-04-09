import requests
import json
import sqlite3

# I will query the database to get an active session and try sending a real HTTP request to http://127.0.0.1:5000
# But I can't easily get the session cookie.
# Instead, let me mock FormData in the test client.

from app import create_app
from models import db, User, MenuItem, CartItem

app = create_app()
with app.app_context():
    user = User.query.filter_by(role='user').first()
    menu_item = MenuItem.query.first()
    
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
            
        print("Sending POST request simulating empty FormData (multipart/form-data)")
        response = client.post(
            f'/user/add_to_cart/{menu_item.id}',
            data={},
            content_type='multipart/form-data',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        print("Status", response.status_code)
        print("Data", response.get_data(as_text=True))
