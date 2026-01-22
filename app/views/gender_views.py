# app/views/gender_views.py
from pyramid.view import view_config
from pyramid.response import Response
import json
from app.database import SessionLocal
from app.models.gender import Gender
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

def format_gender(gender):
    """Convierte un género a diccionario formateado"""
    return {
        'id': gender.id,
        'code': gender.code,
        'name': gender.name,
        'is_active': gender.is_active
    }

@view_config(route_name='list_genders', renderer='json')
def list_genders(request):
    """Lista todos los géneros activos - sin autenticación requerida"""
    try:
        db = SessionLocal()
        genders = db.query(Gender).filter(Gender.is_active == True).all()
        db.close()
        
        return [format_gender(g) for g in genders]
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500)

@view_config(route_name='create_gender', renderer='json')
def create_gender(request):
    """Crear un nuevo género"""
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
        if db.query(Gender).filter(Gender.code == data['code']).first():
            db.close()
            return Response(
                json.dumps({'error': 'Ya existe un género con este código'}),
                status=400
            )
        
        new_gender = Gender(
            code=data['code'],
            name=data['name'],
            is_active=True
        )
        
        db.add(new_gender)
        db.commit()
        db.refresh(new_gender)
        db.close()
        
        return {
            'message': 'Género creado exitosamente',
            'data': format_gender(new_gender)
        }
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500)

@view_config(route_name='get_gender', renderer='json')
def get_gender(request):
    """Obtener un género por ID"""
    try:
        gender_id = int(request.matchdict['id'])
        db = SessionLocal()
        
        gender = db.query(Gender).filter(Gender.id == gender_id).first()
        db.close()
        
        if not gender:
            return Response(json.dumps({'error': 'Género no encontrado'}), status=404)
        
        return format_gender(gender)
    except ValueError:
        return Response(json.dumps({'error': 'ID inválido'}), status=400)
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500)

@view_config(route_name='update_gender', renderer='json')
def update_gender(request):
    """Actualizar un género"""
    user_id, error = get_current_user_id(request)
    if error:
        return error
    
    try:
        gender_id = int(request.matchdict['id'])
        data = request.json_body
        db = SessionLocal()
        
        gender = db.query(Gender).filter(Gender.id == gender_id).first()
        if not gender:
            db.close()
            return Response(json.dumps({'error': 'Género no encontrado'}), status=404)
        
        # Actualizar campos
        if 'name' in data:
            gender.name = data['name']
        if 'is_active' in data:
            gender.is_active = data['is_active']
        
        db.commit()
        db.close()
        
        return {
            'message': 'Género actualizado exitosamente',
            'data': format_gender(gender)
        }
    except ValueError:
        return Response(json.dumps({'error': 'ID inválido'}), status=400)
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500)

@view_config(route_name='delete_gender', renderer='json')
def delete_gender(request):
    """Eliminar un género (soft delete)"""
    user_id, error = get_current_user_id(request)
    if error:
        return error
    
    try:
        gender_id = int(request.matchdict['id'])
        db = SessionLocal()
        
        gender = db.query(Gender).filter(Gender.id == gender_id).first()
        if not gender:
            db.close()
            return Response(json.dumps({'error': 'Género no encontrado'}), status=404)
        
        # Soft delete
        gender.is_active = False
        db.commit()
        db.close()
        
        return {'message': 'Género eliminado exitosamente'}
    except ValueError:
        return Response(json.dumps({'error': 'ID inválido'}), status=400)
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500)