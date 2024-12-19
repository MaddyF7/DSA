# Import create_app function from init.py
from init import create_app
# Set Flask instance from create_app
app = create_app()
# Runs create_app Flask application only on file execution
if __name__ == '__main__':
    app.run(debug=True)