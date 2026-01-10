from pyramid.config import Configurator
from app.database import engine, Base
from app.models.user import User
from app.models.account import Account
from pyramid.static import static_view

# Create tables
Base.metadata.create_all(bind=engine)

def main(global_config, **settings):
    config = Configurator(settings=settings)
    
    # User routes
    config.add_route('create_user', '/api/users', request_method='POST')
    config.add_route('get_user', '/api/users/{id}', request_method='GET')
    config.add_route('list_users', '/api/users', request_method='GET')
    config.add_route('update_user', '/api/users/{id}', request_method='PUT')
    config.add_route('delete_user', '/api/users/{id}', request_method='DELETE')
    
    # Account routes
    config.add_route('register_account', '/api/accounts/register', request_method='POST')
    config.add_route('login', '/api/accounts/login', request_method='POST')
    config.add_route('change_password', '/api/accounts/change-password', request_method='PUT')
    config.add_route('logout', '/api/accounts/logout', request_method='POST')
   
    # Product routes
    config.add_route('create_product', '/api/organizations/{org_id}/products', request_method='POST')
    config.add_route('get_product', '/api/organizations/{org_id}/products/{product_id}', request_method='GET')
    config.add_route('list_products', '/api/organizations/{org_id}/products', request_method='GET')
    config.add_route('update_product', '/api/organizations/{org_id}/products/{product_id}', request_method='PUT')
    config.add_route('delete_product', '/api/organizations/{org_id}/products/{product_id}', request_method='DELETE')
    
    # Scan to register views
    config.scan()
    
    return config.make_wsgi_app()