import os
from flask import Flask, redirect, url_for
from config import Config
from models import User
from extensions import db, login_manager, bcrypt

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_message_category = 'info'

    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import request, redirect, url_for
        if request.blueprint == 'restaurant':
            return redirect(url_for('auth.login', role='restaurant'))
        elif request.blueprint == 'delivery':
            return redirect(url_for('auth.login', role='delivery'))
        return redirect(url_for('auth.login', role='user'))

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from routes.auth_routes import auth_bp
    from routes.user_routes import user_bp
    from routes.restaurant_routes import restaurant_bp
    from routes.delivery_routes import delivery_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/')
    app.register_blueprint(restaurant_bp, url_prefix='/restaurant')
    app.register_blueprint(delivery_bp, url_prefix='/delivery')

    with app.app_context():
        db.create_all()
        # Safe migration for profile_pic
        try:
            db.session.execute(db.text('ALTER TABLE "user" ADD COLUMN profile_pic VARCHAR(250) DEFAULT \'default_profile.png\''))
            db.session.commit()
        except Exception:
            db.session.rollback()

    @app.context_processor
    def inject_global_variables():
        pending_count = 0
        try:
            from flask_login import current_user
            if current_user.is_authenticated and current_user.role == 'restaurant':
                from models import Order
                pending_count = Order.query.filter_by(restaurant_id=current_user.id, status='Pending').count()
        except Exception:
            pass
        return dict(pending_orders_count=pending_count)

    @app.errorhandler(Exception)
    def handle_exception(e):
        import traceback
        try:
            with open('error.log', 'w') as f:
                f.write(traceback.format_exc())
        except Exception:
            pass
        return f"Internal Server Error: {str(e)}", 500

    @app.route('/home')
    @app.route('/user/home')
    def legacy_redirects():
        return redirect(url_for('user.home'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 10000)),
        debug=False
    )