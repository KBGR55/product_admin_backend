from pyramid.view import view_config
from pyramid.response import Response
import json
from app.database import SessionLocal
from app.models.organization import Organization
from app.models.product import Product
from app.middleware.jwt_middleware import extract_token, verify_token

@view_config(route_name='create_product', renderer='json')
def create_product(request):
    try:
        token = extract_token(request)
        if not token:
            return Response(json.dumps({'error': 'Token requerido'}), status=401)
        
        verify_token(token)
        
        org_id = request.matchdict.get('org_id')
        data = request.json_body
        
        db = SessionLocal()
        
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            db.close()
            return Response(json.dumps({'error': 'Organización no encontrada'}), status=404)
        
        product_exists = db.query(Product).filter(
            Product.sku == data['sku'],
            Product.org_id == org_id
        ).first()
        
        if product_exists:
            db.close()
            return Response(json.dumps({'error': 'El SKU ya existe en esta organización'}), status=400)
        
        new_product = Product(
            org_id=org_id,
            name=data['name'],
            description=data.get('description'),
            sku=data['sku'],
            price=data['price'],
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
            'name': new_product.name
        }
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)

@view_config(route_name='get_product', renderer='json')
def get_product(request):
    try:
        token = extract_token(request)
        if not token:
            return Response(json.dumps({'error': 'Token requerido'}), status=401)
        
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
            return Response(json.dumps({'error': 'Producto no encontrado'}), status=404)
        
        return {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'sku': product.sku,
            'price': product.price,
            'cost': product.cost,
            'stock': product.stock,
            'photo_url': product.photo_url,
            'is_active': product.is_active,
            'attributes': product.attributes,
            'created_at': str(product.created_at),
            'updated_at': str(product.updated_at)
        }
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)

@view_config(route_name='list_products', renderer='json')
def list_products(request):
    try:
        token = extract_token(request)
        if not token:
            return Response(json.dumps({'error': 'Token requerido'}), status=401)
        
        verify_token(token)
        
        org_id = request.matchdict.get('org_id')
        
        db = SessionLocal()
        
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            db.close()
            return Response(json.dumps({'error': 'Organización no encontrada'}), status=404)
        
        products = db.query(Product).filter(Product.org_id == org_id).all()
        db.close()
        
        return {
            'products': [
                {
                    'id': p.id,
                    'name': p.name,
                    'description': p.description,
                    'sku': p.sku,
                    'price': p.price,
                    'cost': p.cost,
                    'stock': p.stock,
                    'photo_url': p.photo_url,
                    'is_active': p.is_active,
                    'attributes': p.attributes,
                    'created_at': str(p.created_at)
                }
                for p in products
            ]
        }
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)

@view_config(route_name='update_product', renderer='json')
def update_product(request):
    try:
        token = extract_token(request)
        if not token:
            return Response(json.dumps({'error': 'Token requerido'}), status=401)
        
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
            return Response(json.dumps({'error': 'Producto no encontrado'}), status=404)
        
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = data.get('price', product.price)
        product.cost = data.get('cost', product.cost)
        product.stock = data.get('stock', product.stock)
        product.photo_url = data.get('photo_url', product.photo_url)
        product.is_active = data.get('is_active', product.is_active)
        
        if 'attributes' in data:
            product.attributes = data['attributes']
        
        db.commit()
        db.close()
        
        return {'message': 'Producto actualizado exitosamente'}
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)

@view_config(route_name='delete_product', renderer='json')
def delete_product(request):
    try:
        token = extract_token(request)
        if not token:
            return Response(json.dumps({'error': 'Token requerido'}), status=401)
        
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
            return Response(json.dumps({'error': 'Producto no encontrado'}), status=404)
        
        db.delete(product)
        db.commit()
        db.close()
        
        return {'message': 'Producto eliminado exitosamente'}
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)