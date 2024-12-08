"""
Application entry point.
Initializes and runs the Flask application with database creation.

Features:
    - Creates Flask application instance
    - Initializes database tables
    - Runs development server with debug mode
"""
from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)