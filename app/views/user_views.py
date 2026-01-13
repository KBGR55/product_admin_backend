# app/views/user_views.py
from pyramid.view import view_config
from pyramid.response import Response
import json
from app.database import SessionLocal
from app.models.user import User, IdentityType, Gender
from app.middleware.jwt_middleware import extract_token, verify_token
from datetime import datetime

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

def format_user(user):
    """Convierte un usuario a diccionario formateado"""
    return {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'birth_date': user.birth_date.isoformat(),
        'identity_number': user.identity_number,
        'identity_type': user.identity_type.value,
        'gender': user.gender.value,
        'is_active': user.is_active,
        'created_at': user.created_at.isoformat()
    }

@view_config(route_name='create_user', renderer='json')
def create_user(request):
    try:
        data = request.json_body
        db = SessionLocal()
        
        # Validar campos requeridos
        required_fields = ['first_name', 'last_name', 'birth_date', 'identity_number', 'identity_type', 'gender']
        missing = [f for f in required_fields if f not in data]
        if missing:
            db.close()
            return Response(
                json.dumps({'error': f'Campos requeridos faltantes: {", ".join(missing)}'}),
                status=400
            )
        
        # Validar que el usuario no exista
        if db.query(User).filter(User.identity_number == data['identity_number']).first():
            db.close()
            return Response(
                json.dumps({'error': 'El usuario con este número de identidad ya existe'}),
                status=400
            )
        
        # Validar enum values
        try:
            identity_type = IdentityType[data['identity_type']]
            gender = Gender[data['gender']]
        except KeyError as e:
            db.close()
            return Response(
                json.dumps({'error': f'Valor inválido para enum: {str(e)}'}),
                status=400
            )
        
        # Validar formato de fecha
        try:
            birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        except ValueError:
            db.close()
            return Response(
                json.dumps({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}),
                status=400
            )
        
        new_user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            birth_date=birth_date,
            identity_number=data['identity_number'],
            identity_type=identity_type,
            gender=gender,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        db.close()
        
        return {
            'message': 'Usuario creado exitosamente',
            'user_id': new_user.id
        }
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500)

@view_config(route_name='get_user', renderer='json')
def get_user(request):
    user_id, error = get_current_user_id(request)
    if error:
        return error
    
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        db.close()
        
        if not user:
            return Response(json.dumps({'error': 'Usuario no encontrado'}), status=404)
        
        return format_user(user)
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500)

@view_config(route_name='list_users', renderer='json')
def list_users(request):
    user_id, error = get_current_user_id(request)
    if error:
        return error
    
    try:
        db = SessionLocal()
        users = db.query(User).filter(User.is_active == True).all()
        db.close()
        
        return {
            'users': [format_user(u) for u in users]
        }
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500)

@view_config(route_name='update_user', renderer='json')
def update_user(request):
    user_id, error = get_current_user_id(request)
    if error:
        return error
    
    try:
        data = request.json_body
        db = SessionLocal()
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            db.close()
            return Response(json.dumps({'error': 'Usuario no encontrado'}), status=404)
        
        # Actualizar campos simples
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        # Actualizar birth_date con validación
        if 'birth_date' in data:
            try:
                user.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
            except ValueError:
                db.close()
                return Response(
                    json.dumps({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}),
                    status=400
                )
        
        # Actualizar gender con validación
        if 'gender' in data:
            try:
                user.gender = Gender[data['gender']]
            except KeyError:
                db.close()
                return Response(
                    json.dumps({'error': f'Valor inválido para gender: {data["gender"]}'}),
                    status=400
                )
        
        db.commit()
        db.close()
        
        return {'message': 'Usuario actualizado exitosamente'}
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500)

@view_config(route_name='delete_user', renderer='json')
def delete_user(request):
    user_id, error = get_current_user_id(request)
    if error:
        return error
    
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            db.close()
            return Response(json.dumps({'error': 'Usuario no encontrado'}), status=404)
        
        # Soft delete - marcar como inactivo
        user.is_active = False
        db.commit()
        db.close()
        
        return {'message': 'Usuario eliminado exitosamente'}
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500)