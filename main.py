import os
from waitress import serve
from app import main as app_factory

if __name__ == '__main__':
    app = app_factory({})

    port = int(os.environ.get("PORT", 6543))
    host = "0.0.0.0"

    print(f"Server starting at http://{host}:{port}")
    serve(app, host=host, port=port)