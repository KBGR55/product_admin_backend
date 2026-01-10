from pyramid.view import view_config
from pyramid.response import Response
import json
from app.database import SessionLocal
from app.models.user import User
from app.models.account import Account
from app.middleware.jwt_middleware import create_token, extract_token, verify_token

@view_config(route_name='register_account', renderer='json')
def register_account(request):
    try:
        data = request.json_body
        db = SessionLocal()
        
        user = db.query(User).filter(User.id == data['user_id']).first()
        if not user:
            db.close()
            return Response(json.dumps({'error': 'Usuario no encontrado'}), status=404)
        
        account_exists = db.query(Account).filter(Account.email == data['email']).first()
        if account_exists:
            db.close()
            return Response(json.dumps({'error': 'El correo ya está registrado'}), status=400)
        
        new_account = Account(user_id=user.id, email=data['email'])
        new_account.set_password(data['password'])
        
        db.add(new_account)
        db.commit()
        db.close()
        
        return {'message': 'Cuenta creada exitosamente'}
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)

@view_config(route_name='login', renderer='json')
def login(request):
    try:
        data = request.json_body
        db = SessionLocal()
        
        account = db.query(Account).filter(Account.email == data['email']).first()
        if not account or not account.verify_password(data['password']):
            db.close()
            return Response(json.dumps({'error': 'Correo o contraseña incorrectos'}), status=401)
        
        token = create_token({'user_id': account.user_id, 'email': account.email})
        db.close()
        
        return {
            'message': 'Inicio de sesión exitoso',
            'token': token,
            'user_id': account.user_id
        }
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)

@view_config(route_name='change_password', renderer='json')
def change_password(request):
    try:
        token = extract_token(request)
        if not token:
            return Response(json.dumps({'error': 'Token requerido'}), status=401)
        
        payload = verify_token(token)
        user_id = payload.get('user_id')
        
        data = request.json_body
        db = SessionLocal()
        
        account = db.query(Account).filter(Account.user_id == user_id).first()
        if not account:
            db.close()
            return Response(json.dumps({'error': 'Cuenta no encontrada'}), status=404)
        
        if not account.verify_password(data['current_password']):
            db.close()
            return Response(json.dumps({'error': 'Contraseña actual incorrecta'}), status=401)
        
        account.set_password(data['new_password'])
        db.commit()
        db.close()
        
        return {'message': 'Contraseña actualizada exitosamente'}
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)

@view_config(route_name='logout', renderer='json')
def logout(request):
    return {'message': 'Sesión cerrada exitosamente'}