from pyramid.view import view_config
from pyramid.response import Response
import json
from app.database import SessionLocal
from app.models.user import User, IdentityType, Gender
from app.middleware.jwt_middleware import extract_token, verify_token
from datetime import datetime

@view_config(route_name='create_user', renderer='json')
def create_user(request):
    try:
        data = request.json_body
        db = SessionLocal()
        
        # Validate user doesn't exist
        user_exists = db.query(User).filter(
            User.identity_number == data['identity_number']
        ).first()
        
        if user_exists:
            db.close()
            return Response(
                json.dumps({'error': 'El usuario con este número de identidad ya existe'}),
                status=400
            )
        
        new_user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d').date(),
            identity_number=data['identity_number'],
            identity_type=IdentityType[data['identity_type']],
            gender=Gender[data['gender']]
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
        return Response(json.dumps({'error': str(e)}), status=400)

@view_config(route_name='get_user', renderer='json')
def get_user(request):
    try:
        token = extract_token(request)
        if not token:
            return Response(json.dumps({'error': 'Token requerido'}), status=401)
        
        payload = verify_token(token)
        user_id = payload.get('user_id')
        
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        db.close()
        
        if not user:
            return Response(json.dumps({'error': 'Usuario no encontrado'}), status=404)
        
        return {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'birth_date': str(user.birth_date),
            'identity_number': user.identity_number,
            'identity_type': user.identity_type.value,
            'gender': user.gender.value
        }
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)

@view_config(route_name='list_users', renderer='json')
def list_users(request):
    try:
        token = extract_token(request)
        if not token:
            return Response(json.dumps({'error': 'Token requerido'}), status=401)
        
        verify_token(token)
        
        db = SessionLocal()
        users = db.query(User).all()
        db.close()
        
        return {
            'users': [
                {
                    'id': u.id,
                    'first_name': u.first_name,
                    'last_name': u.last_name,
                    'birth_date': str(u.birth_date),
                    'identity_number': u.identity_number,
                    'identity_type': u.identity_type.value,
                    'gender': u.gender.value
                }
                for u in users
            ]
        }
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)

@view_config(route_name='update_user', renderer='json')
def update_user(request):
    try:
        token = extract_token(request)
        if not token:
            return Response(json.dumps({'error': 'Token requerido'}), status=401)
        
        payload = verify_token(token)
        user_id = payload.get('user_id')
        
        data = request.json_body
        db = SessionLocal()
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            db.close()
            return Response(json.dumps({'error': 'Usuario no encontrado'}), status=404)
        
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        if 'birth_date' in data:
            user.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        if 'gender' in data:
            user.gender = Gender[data['gender']]
        
        db.commit()
        db.close()
        
        return {'message': 'Usuario actualizado exitosamente'}
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)

@view_config(route_name='delete_user', renderer='json')
def delete_user(request):
    try:
        token = extract_token(request)
        if not token:
            return Response(json.dumps({'error': 'Token requerido'}), status=401)
        
        payload = verify_token(token)
        user_id = payload.get('user_id')
        
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            db.close()
            return Response(json.dumps({'error': 'Usuario no encontrado'}), status=404)
        
        db.delete(user)
        db.commit()
        db.close()
        
        return {'message': 'Usuario eliminado exitosamente'}
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)