from pyramid.config import Configurator
from pyramid.response import Response
from app.database import engine, Base
from app.models.user import User
from app.models.account import Account
from app.models.organization import Organization, OrganizationRole, OrganizationEmployee
from app.models.product import Product
from app.models.identity_type import IdentityType
from app.models.gender import Gender


# Create tables
# Base.metadata.create_all(bind=engine)

def main(global_config, **settings):
    config = Configurator(settings=settings)
    
    # CORS Configuration
    def add_cors_headers(event):
        response = event.response
        response.headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS, PUT, DELETE',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600',
        })
    
    config.add_subscriber(add_cors_headers, 'pyramid.events.NewResponse')
    
    # Handle preflight requests
    config.add_route('cors_options', '/{path_info:.*}', request_method='OPTIONS')
    
    def cors_options_handler(request):
        return Response(status=200)
    
    config.add_view(cors_options_handler, route_name='cors_options')
    
    # ==================== RUTAS PÚBLICAS (sin autenticación) ====================
    config.add_route('list_public_organizations', '/api/public/organizations', request_method='GET')
    config.add_route('list_products_public', '/api/public/organizations/{org_id}/products', request_method='GET')

    # ==================== User routes ====================
    config.add_route('create_user', '/api/users', request_method='POST')
    config.add_route('get_user', '/api/users/{id}', request_method='GET')
    config.add_route('list_users', '/api/users', request_method='GET')
    config.add_route('update_user', '/api/users/{id}', request_method='PUT')
    config.add_route('delete_user', '/api/users/{id}', request_method='DELETE')
    
    # ==================== Account routes ====================
    config.add_route('register_account', '/api/accounts/register', request_method='POST')
    config.add_route('login', '/api/accounts/login', request_method='POST')
    config.add_route('change_password', '/api/accounts/change-password', request_method='PUT')
    config.add_route('logout', '/api/accounts/logout', request_method='POST')
       
    # ==================== Organization routes ====================
    config.add_route('create_org', '/api/organizations', request_method='POST')
    config.add_route('get_org', '/api/organizations/{org_id}', request_method='GET')
    config.add_route('list_org', '/api/organizations', request_method='GET')
    config.add_route('update_org', '/api/organizations/{org_id}', request_method='PUT')
    config.add_route('delete_org', '/api/organizations/{org_id}', request_method='DELETE')
    
    # ==================== Organization Employee routes ====================
    config.add_route('add_employee', '/api/organizations/{org_id}/employees', request_method='POST')
    config.add_route('remove_employee', '/api/organizations/{org_id}/employees/{employee_id}', request_method='DELETE')
    config.add_route('list_employees', '/api/organizations/{org_id}/employees', request_method='GET')
    
    # ==================== Organization Role routes ====================
    config.add_route('create_org_role', '/api/organizations/{org_id}/roles', request_method='POST')
    config.add_route('list_org_roles', '/api/organizations/{org_id}/roles', request_method='GET')
    config.add_route('assign_org_role', '/api/organizations/{org_id}/employees/{employee_id}/roles/{role_id}', request_method='POST')
    config.add_route('remove_org_role', '/api/organizations/{org_id}/employees/{employee_id}/roles/{role_id}', request_method='DELETE')
    
    # ==================== Product routes ====================
    config.add_route('create_product', '/api/organizations/{org_id}/products', request_method='POST')
    config.add_route('get_product', '/api/organizations/{org_id}/products/{product_id}', request_method='GET')
    config.add_route('list_products', '/api/organizations/{org_id}/products', request_method='GET')
    config.add_route('update_product', '/api/organizations/{org_id}/products/{product_id}', request_method='PUT')
    config.add_route('delete_product', '/api/organizations/{org_id}/products/{product_id}', request_method='DELETE')
    
    # IDENTITY TYPES ROUTES
    config.add_route('list_identity_types', '/api/identity-types', request_method='GET')
    config.add_route('create_identity_type', '/api/identity-types', request_method='POST')
    config.add_route('get_identity_type', '/api/identity-types/{id}', request_method='GET')
    config.add_route('update_identity_type', '/api/identity-types/{id}', request_method='PUT')
    config.add_route('delete_identity_type', '/api/identity-types/{id}', request_method='DELETE')

    # GENDERS ROUTES
    config.add_route('list_genders', '/api/genders', request_method='GET')
    config.add_route('create_gender', '/api/genders', request_method='POST')
    config.add_route('get_gender', '/api/genders/{id}', request_method='GET')
    config.add_route('update_gender', '/api/genders/{id}', request_method='PUT')
    config.add_route('delete_gender', '/api/genders/{id}', request_method='DELETE')


    # Scan all view modules to register views
    config.scan('app.views')
    
    return config.make_wsgi_app()