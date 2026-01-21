from pyramid.view import view_config
from pyramid.response import Response
import json
from decimal import Decimal
from app.database import SessionLocal
from app.models.product import Product
from app.models.organization import Organization
from app.middleware.jwt_middleware import extract_token, verify_token

# ==================== FUNCIONES AUXILIARES ====================

def json_response(data, status=200):
    """Crea una respuesta JSON correctamente formateada"""
    return Response(
        json.dumps(data),
        status=status,
        content_type='application/json; charset=utf-8'
    )

def convert_decimal_to_float(obj):
    """Convierte Decimal a float para JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def format_product(product):
    """Formatea un producto para retornarlo en JSON"""
    return {
        'id': product.id,
        'org_id': product.org_id,
        'name': product.name,
        'description': product.description,
        'sku': product.sku,
        'price': float(product.price),  # Convertir Decimal a float
        'cost': float(product.cost) if product.cost else None,
        'stock': product.stock,
        'photo_url': product.photo_url,
        'is_active': product.is_active,
        'attributes': product.attributes or {},
        'created_at': product.created_at.isoformat(),
        'updated_at': product.updated_at.isoformat()
    }

# ==================== RUTAS ====================
@view_config(route_name='list_products_public', renderer='json', request_method='GET')
def list_products_public(request):
    """Lista todos los productos de una organización (PÚBLICO - sin autenticación)"""
    try:
        org_id = request.matchdict.get('org_id')
        
        db = SessionLocal()
        
        # Validar que la organización existe y está activa
        org = db.query(Organization).filter(
            Organization.id == org_id,
            Organization.is_active == True
        ).first()
        
        if not org:
            db.close()
            return json_response({'error': 'Organización no encontrada'}, status=404)
        
        # Obtener solo productos activos
        products = db.query(Product).filter(
            Product.org_id == org_id,
            Product.is_active == True
        ).all()
        db.close()
        
        return {
            'products': [format_product(p) for p in products],
            'count': len(products)
        }
    
    except Exception as e:
        return json_response({'error': str(e)}, status=500)

@view_config(route_name='create_product', renderer='json', request_method='POST')
def create_product(request):
    """Crea un nuevo producto"""
    try:
        token = extract_token(request)
        if not token:
            return json_response({'error': 'Token requerido'}, status=401)
        
        verify_token(token)
        
        org_id = request.matchdict.get('org_id')
        data = request.json_body
        
        db = SessionLocal()
        
        # Validar que la organización existe
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            db.close()
            return json_response({'error': 'Organización no encontrada'}, status=404)
        
        # Crear producto sin SKU (se generará automáticamente)
        new_product = Product(
            org_id=org_id,
            name=data.get('name'),
            description=data.get('description'),
            sku=data.get('sku'),
            price=data.get('price'),
            cost=data.get('cost'),
            stock=data.get('stock', 0),
            photo_url=data.get('photo_url'),
            is_active=data.get('is_active', True),
            attributes=data.get('attributes', {})
        )
        
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        db.close()
        
        return {
            'message': 'Producto creado exitosamente',
            'product_id': new_product.id,
            'name': new_product.name,
            'sku': new_product.sku
        }
    
    except KeyError as e:
        return json_response({'error': f'Campo requerido faltante: {str(e)}'}, status=400)
    except Exception as e:
        return json_response({'error': str(e)}, status=500)

@view_config(route_name='get_product', renderer='json', request_method='GET')
def get_product(request):
    """Obtiene un producto específico"""
    try:
        token = extract_token(request)
        if not token:
            return json_response({'error': 'Token requerido'}, status=401)
        
        verify_token(token)
        
        org_id = request.matchdict.get('org_id')
        product_id = request.matchdict.get('product_id')
        
        db = SessionLocal()
        
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.org_id == org_id
        ).first()
        
        db.close()
        
        if not product:
            return json_response({'error': 'Producto no encontrado'}, status=404)
        
        return format_product(product)
    
    except Exception as e:
        return json_response({'error': str(e)}, status=500)

@view_config(route_name='list_products', renderer='json', request_method='GET')
def list_products(request):
    """Lista todos los productos de una organización"""
    try:
        token = extract_token(request)
        if not token:
            return json_response({'error': 'Token requerido'}, status=401)
        
        verify_token(token)
        
        org_id = request.matchdict.get('org_id')
        
        db = SessionLocal()
        
        # Validar que la organización existe
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            db.close()
            return json_response({'error': 'Organización no encontrada'}, status=404)
        
        products = db.query(Product).filter(Product.org_id == org_id).all()
        db.close()
        
        return {
            'products': [format_product(p) for p in products],
            'count': len(products)
        }
    
    except Exception as e:
        return json_response({'error': str(e)}, status=500)

@view_config(route_name='update_product', renderer='json', request_method='PUT')
def update_product(request):
    """Actualiza un producto"""
    try:
        token = extract_token(request)
        if not token:
            return json_response({'error': 'Token requerido'}, status=401)
        
        verify_token(token)
        
        org_id = request.matchdict.get('org_id')
        product_id = request.matchdict.get('product_id')
        data = request.json_body
        
        db = SessionLocal()
        
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.org_id == org_id
        ).first()
        
        if not product:
            db.close()
            return json_response({'error': 'Producto no encontrado'}, status=404)
        
        updatable_fields = [
            'name', 'description', 'price', 'cost',
            'stock', 'photo_url', 'is_active', 'attributes'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(product, field, data[field])
        
        db.commit()
        db.refresh(product)
        db.close()
        
        return {
            'message': 'Producto actualizado exitosamente',
            'product': format_product(product)
        }
    
    except Exception as e:
        return json_response({'error': str(e)}, status=500)

@view_config(route_name='delete_product', renderer='json', request_method='DELETE')
def delete_product(request):
    """Elimina un producto"""
    try:
        token = extract_token(request)
        if not token:
            return json_response({'error': 'Token requerido'}, status=401)
        
        verify_token(token)
        
        org_id = request.matchdict.get('org_id')
        product_id = request.matchdict.get('product_id')
        
        db = SessionLocal()
        
        product = db.query(Product).filter(
            Product.id == product_id,
            Product.org_id == org_id
        ).first()
        
        if not product:
            db.close()
            return json_response({'error': 'Producto no encontrado'}, status=404)
        
        db.delete(product)
        db.commit()
        db.close()
        
        return {'message': 'Producto eliminado exitosamente'}
    
    except Exception as e:
        return json_response({'error': str(e)}, status=500)