# app/views/country_views.py
from pyramid.view import view_config
from pyramid.response import Response
import json
from app.database import SessionLocal
from app.models.country import Country
from app.middleware.jwt_middleware import extract_token, verify_token

def get_current_user_id(request, require_token=True):
    """Extrae y valida el token, retorna el user_id"""
    token = extract_token(request)
    if not token:
        if require_token:
            return None, Response(json.dumps({'error': 'Token requerido'}), status=401)
        return None, None
    
    try:
        payload = verify_token(token)
        return payload.get('user_id'), None
    except Exception as e:
        return None, Response(json.dumps({'error': str(e)}), status=400)

def format_country(country):
    """Convierte un país a diccionario formateado"""
    return {
        'id': country.id,
        'code': country.code,
        'name': country.name,
        'phone_code': country.phone_code,
        'is_active': country.is_active
    }

@view_config(route_name='list_countries', renderer='json')
def list_countries(request):
    """Lista todos los países activos - devuelve array directo"""
    try:
        db = SessionLocal()
        # Filtrar activos (True o NULL se considera activo)
        countries = db.query(Country)\
            .filter((Country.is_active == True) | (Country.is_active == None))\
            .all()
        db.close()

        # Devuelve directamente el array
        return [format_country(c) for c in countries]

    except Exception as e:
        request.response.status = 500
        return {'error': str(e)}

@view_config(route_name='create_country', renderer='json')
def create_country(request):
    """Crear un nuevo país"""
    user_id, error = get_current_user_id(request)
    if error:
        return error
    
    try:
        data = request.json_body
        db = SessionLocal()
        
        # Validar campos requeridos
        if not data.get('code') or not data.get('name') or not data.get('phone_code'):
            db.close()
            return Response(
                json.dumps({'error': 'Los campos code, name y phone_code son requeridos'}),
                status=400
            )
        
        # Validar que no exista
        if db.query(Country).filter(Country.code == data['code']).first():
            db.close()
            return Response(
                json.dumps({'error': 'Ya existe un país con este código'}),
                status=400
            )
        
        new_country = Country(
            code=data['code'],
            name=data['name'],
            phone_code=data['phone_code'],
            is_active=True
        )
        
        db.add(new_country)
        db.commit()
        db.refresh(new_country)
        db.close()
        
        return {
            'message': 'País creado exitosamente',
            'data': format_country(new_country)
        }
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500)

@view_config(route_name='get_country', renderer='json')
def get_country(request):
    """Obtener un país por ID"""
    try:
        country_id = int(request.matchdict['id'])
        db = SessionLocal()
        
        country = db.query(Country).filter(Country.id == country_id).first()
        db.close()
        
        if not country:
            return Response(json.dumps({'error': 'País no encontrado'}), status=404)
        
        return format_country(country)
    except ValueError:
        return Response(json.dumps({'error': 'ID inválido'}), status=400)
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500)

@view_config(route_name='update_country', renderer='json')
def update_country(request):
    """Actualizar un país"""
    user_id, error = get_current_user_id(request)
    if error:
        return error
    
    try:
        country_id = int(request.matchdict['id'])
        data = request.json_body
        db = SessionLocal()
        
        country = db.query(Country).filter(Country.id == country_id).first()
        if not country:
            db.close()
            return Response(json.dumps({'error': 'País no encontrado'}), status=404)
        
        # Actualizar campos
        if 'name' in data:
            country.name = data['name']
        if 'phone_code' in data:
            country.phone_code = data['phone_code']
        if 'is_active' in data:
            country.is_active = data['is_active']
        
        db.commit()
        db.close()
        
        return {
            'message': 'País actualizado exitosamente',
            'data': format_country(country)
        }
    except ValueError:
        return Response(json.dumps({'error': 'ID inválido'}), status=400)
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500)

@view_config(route_name='delete_country', renderer='json')
def delete_country(request):
    """Eliminar un país (soft delete)"""
    user_id, error = get_current_user_id(request)
    if error:
        return error
    
    try:
        country_id = int(request.matchdict['id'])
        db = SessionLocal()
        
        country = db.query(Country).filter(Country.id == country_id).first()
        if not country:
            db.close()
            return Response(json.dumps({'error': 'País no encontrado'}), status=404)
        
        # Soft delete
        country.is_active = False
        db.commit()
        db.close()
        
        return {'message': 'País eliminado exitosamente'}
    except ValueError:
        return Response(json.dumps({'error': 'ID inválido'}), status=400)
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500)