# app/views/identity_type_views.py
from pyramid.view import view_config
from pyramid.response import Response
import json
from app.database import SessionLocal
from app.models.identity_type import IdentityType
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

def format_identity_type(identity_type):
    """Convierte un tipo de identidad a diccionario formateado"""
    return {
        'id': identity_type.id,
        'code': identity_type.code,
        'name': identity_type.name,
        'is_active': identity_type.is_active
    }

@view_config(route_name='list_identity_types', renderer='json')
def list_identity_types(request):
    """Lista todos los tipos de identidad activos - sin autenticación requerida"""
    try:
        db = SessionLocal()
        identity_types = db.query(IdentityType).filter(IdentityType.is_active == True).all()
        db.close()
        
        return [format_identity_type(it) for it in identity_types]
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500)

@view_config(route_name='create_identity_type', renderer='json')
def create_identity_type(request):
    """Crear un nuevo tipo de identidad"""
    user_id, error = get_current_user_id(request)
    if error:
        return error
    
    try:
        data = request.json_body
        db = SessionLocal()
        
        # Validar campos requeridos
        if not data.get('code') or not data.get('name'):
            db.close()
            return Response(
                json.dumps({'error': 'Los campos code y name son requeridos'}),
                status=400
            )
        
        # Validar que no exista
        if db.query(IdentityType).filter(IdentityType.code == data['code']).first():
            db.close()
            return Response(
                json.dumps({'error': 'Ya existe un tipo de identidad con este código'}),
                status=400
            )
        
        new_identity_type = IdentityType(
            code=data['code'],
            name=data['name'],
            is_active=True
        )
        
        db.add(new_identity_type)
        db.commit()
        db.refresh(new_identity_type)
        db.close()
        
        return {
            'message': 'Tipo de identidad creado exitosamente',
            'data': format_identity_type(new_identity_type)
        }
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500)

@view_config(route_name='get_identity_type', renderer='json')
def get_identity_type(request):
    """Obtener un tipo de identidad por ID"""
    try:
        identity_type_id = int(request.matchdict['id'])
        db = SessionLocal()
        
        identity_type = db.query(IdentityType).filter(IdentityType.id == identity_type_id).first()
        db.close()
        
        if not identity_type:
            return Response(json.dumps({'error': 'Tipo de identidad no encontrado'}), status=404)
        
        return format_identity_type(identity_type)
    except ValueError:
        return Response(json.dumps({'error': 'ID inválido'}), status=400)
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500)

@view_config(route_name='update_identity_type', renderer='json')
def update_identity_type(request):
    """Actualizar un tipo de identidad"""
    user_id, error = get_current_user_id(request)
    if error:
        return error
    
    try:
        identity_type_id = int(request.matchdict['id'])
        data = request.json_body
        db = SessionLocal()
        
        identity_type = db.query(IdentityType).filter(IdentityType.id == identity_type_id).first()
        if not identity_type:
            db.close()
            return Response(json.dumps({'error': 'Tipo de identidad no encontrado'}), status=404)
        
        # Actualizar campos
        if 'name' in data:
            identity_type.name = data['name']
        if 'is_active' in data:
            identity_type.is_active = data['is_active']
        
        db.commit()
        db.close()
        
        return {
            'message': 'Tipo de identidad actualizado exitosamente',
            'data': format_identity_type(identity_type)
        }
    except ValueError:
        return Response(json.dumps({'error': 'ID inválido'}), status=400)
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500)

@view_config(route_name='delete_identity_type', renderer='json')
def delete_identity_type(request):
    """Eliminar un tipo de identidad (soft delete)"""
    user_id, error = get_current_user_id(request)
    if error:
        return error
    
    try:
        identity_type_id = int(request.matchdict['id'])
        db = SessionLocal()
        
        identity_type = db.query(IdentityType).filter(IdentityType.id == identity_type_id).first()
        if not identity_type:
            db.close()
            return Response(json.dumps({'error': 'Tipo de identidad no encontrado'}), status=404)
        
        # Soft delete
        identity_type.is_active = False
        db.commit()
        db.close()
        
        return {'message': 'Tipo de identidad eliminado exitosamente'}
    except ValueError:
        return Response(json.dumps({'error': 'ID inválido'}), status=400)
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500)