# Import Flask for creating web application
from flask import Flask
# Import MySQL to connect to MySQL database
from flask_mysqldb import MySQL
# Import the Config class to load MySQL database from configuration.py
from configuration import Config
# Create a MySQL instance
mysql = MySQL()
# create_app function
def create_app():
    # Create a Flask instance
    app = Flask(__name__)
    # Load configurations from Config class for MySQL connection
    app.config.from_object(Config)
    # Initialise MySQL connection to Flask app
    mysql.init_app(app)
    # Import blueprint for routes
    from routes import main_bp
    # Register blueprint's routes
    app.register_blueprint(main_bp)
    return app