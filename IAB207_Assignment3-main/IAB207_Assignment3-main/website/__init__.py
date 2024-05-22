from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

db = SQLAlchemy()

def create_app():
    # Load environment variables from .env file
    load_dotenv()

    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'somesecretgoeshere')  # Fallback to a default value if not set
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///mydbname.sqlite')  # Fallback to a default value if not set
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', '/static/image')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Recommended to disable to save resources
    
    # Initialize extensions
    db.init_app(app)
    bootstrap = Bootstrap(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Create a user loader function that takes user ID and returns User
    from .models import User  # Importing here to avoid circular references
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from . import views
    app.register_blueprint(views.bp)

    from . import auth
    app.register_blueprint(auth.authbp)
    
    from . import event
    app.register_blueprint(event.eventbp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html", error=e)

    @app.errorhandler(500)
    def special_exception_handler(e):
        return render_template("500.html", error=e)
    
    return app
