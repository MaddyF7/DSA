import os
# Configure MySQL database connection
class Config:
    # Dynamically retrives secret key from environment variable or uses a fallback value
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key')
    MYSQL_HOST = 'localhost' # Change to host
    MYSQL_USER = 'root' # Change to user
    MYSQL_PASSWORD = 'LilaDoodle0707!' # Change to password
    MYSQL_DB = 'dsa_tracker'