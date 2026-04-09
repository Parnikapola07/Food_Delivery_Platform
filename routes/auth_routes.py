from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from extensions import db, bcrypt

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login/<role>', methods=['GET', 'POST'])
def login(role):
    if role not in ['user', 'restaurant', 'delivery']:
        flash('Invalid role specified.', 'danger')
        return redirect(url_for('user.home'))

    if current_user.is_authenticated:
        if current_user.role == 'restaurant':
            return redirect(url_for('restaurant.dashboard'))
        elif current_user.role == 'delivery':
            return redirect(url_for('delivery.dashboard'))
        return redirect(url_for('user.home'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, role=role).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            if role == 'restaurant':
                return redirect(url_for('restaurant.dashboard'))
            elif role == 'delivery':
                return redirect(url_for('delivery.dashboard'))
            return redirect(url_for('user.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
            
    template = f'auth/login_{role}.html'
    return render_template(template)

@auth_bp.route('/register/<role>', methods=['GET', 'POST'])
def register(role):
    if role not in ['user', 'restaurant', 'delivery']:
        flash('Invalid role specified.', 'danger')
        return redirect(url_for('user.home'))

    if current_user.is_authenticated:
        if current_user.role == 'restaurant':
            return redirect(url_for('restaurant.dashboard'))
        elif current_user.role == 'delivery':
            return redirect(url_for('delivery.dashboard'))
        return redirect(url_for('user.home'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists.', 'danger')
            return redirect(url_for('auth.register', role=role))
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            username=username, 
            email=email, 
            password=hashed_password, 
            role=role,
            phone=phone,
            address=address
        )
        db.session.add(new_user)
        db.session.commit()
        flash(f'Account created for {username}! You can now log in.', 'success')
        return redirect(url_for('auth.login', role=role))
        
    template = f'auth/register_{role}.html'
    return render_template(template)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user.home'))
