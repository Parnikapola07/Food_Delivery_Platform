from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from extensions import db, bcrypt

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/role-select')
def role_select():
    return render_template('role_select.html')

@auth_bp.route('/login/<role>', methods=['GET', 'POST'])
def login(role):
    if role not in ['user', 'restaurant', 'delivery']:
        flash('Invalid role specified.', 'danger')
        return redirect(url_for('user.home'))

    if current_user.is_authenticated:
        if current_user.role == role:
            if role == 'restaurant':
                return redirect(url_for('restaurant.dashboard'))
            elif role == 'delivery':
                return redirect(url_for('delivery.dashboard'))
            return redirect(url_for('user.home'))
        else:
            logout_user()
    
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
        if current_user.role == role:
            if role == 'restaurant':
                return redirect(url_for('restaurant.dashboard'))
            elif role == 'delivery':
                return redirect(url_for('delivery.dashboard'))
            return redirect(url_for('user.home'))
        else:
            logout_user()
        
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
        new_user = User()
        new_user.username = username
        new_user.email = email
        new_user.password = hashed_password
        new_user.role = role
        new_user.phone = phone
        new_user.address = address
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

import os
from werkzeug.utils import secure_filename

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Identify which layout template to extend
    layout_template = 'base_user.html'
    if current_user.role == 'restaurant':
        layout_template = 'base_restaurant.html'
    elif current_user.role == 'delivery':
        layout_template = 'base_delivery.html'

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            username = request.form.get('username')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')
            
            # Check email availability
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != current_user.id:
                flash('Email is already taken by another account.', 'danger')
                return redirect(url_for('auth.profile'))
                
            # Handle profile pic file upload
            profile_pic_file = request.files.get('profile_pic')
            if profile_pic_file and profile_pic_file.filename != '':
                filename = secure_filename(f"profile_{current_user.id}_{profile_pic_file.filename}")
                upload_path = os.path.join('static', 'uploads')
                os.makedirs(upload_path, exist_ok=True)
                profile_pic_file.save(os.path.join(upload_path, filename))
                current_user.profile_pic = f"/static/uploads/{filename}"
                
            current_user.username = username
            current_user.email = email
            current_user.phone = phone
            current_user.address = address
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            
        elif action == 'change_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not bcrypt.check_password_hash(current_user.password, current_password):
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('auth.profile'))
                
            if new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
                return redirect(url_for('auth.profile'))
                
            hashed_pw = bcrypt.generate_password_hash(new_password).decode('utf-8')
            current_user.password = hashed_pw
            db.session.commit()
            flash('Password changed successfully!', 'success')
            
        return redirect(url_for('auth.profile'))
        
    return render_template('auth/profile.html', layout_template=layout_template)
