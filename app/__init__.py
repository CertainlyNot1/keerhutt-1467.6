from flask import Flask
from .extensions import db, bcrypt, login_manager, migrate, dirty_sock

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///kood.db'
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    migrate.init_app(app, db)
    dirty_sock.init_app(app)
    
    

    # Register blueprints
    from .auth.routes import auth_bp
    from .main.routes import main_bp
    from .quiz.routes import quiz_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(quiz_bp)

    return app