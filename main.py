from waitress import serve
from app import main as app_factory

if __name__ == '__main__':
    app = app_factory({})
    print("Server starting at http://localhost:6543")
    serve(app, host='0.0.0.0', port=6543)