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

    @app.route('/home')
    @app.route('/user/home')
    @app.route('/role-select')
    @app.route('/auth/role-select')
    def legacy_redirects():
        return redirect(url_for('user.home'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
