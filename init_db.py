from app import create_app
from extensions import db
import models

print("Starting database initialization...")

app = create_app()

with app.app_context():
    print("Inside app context...")
    db.create_all()
    print("Database created successfully!")