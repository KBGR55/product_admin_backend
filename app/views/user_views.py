from pyramid.view import view_config
from pyramid.response import Response
import json
from app.database import SessionLocal
from app.models.user import User, IdentityType, Gender
from app.middleware.jwt_middleware import extract_token, verify_token
from datetime import datetime

@view_config(route_name='create_user', renderer='json')
def create_user(request):
    """
    Crear un nuevo usuario
    ---
    tags:
      - Usuarios
    summary: Crear usuario
    description: Crea un nuevo usuario en el sistema
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              first_name:
                type: string
                example: Juan
              last_name:
                type: string
                example: Pérez
              birth_date:
                type: string
                format: date
                example: "1990-05-15"
              identity_number:
                type: string
                example: "1234567890"
              identity_type:
                type: string
                enum: [RUC, PASSPORT, FOREIGN_ID]
              gender:
                type: string
                enum: [MALE, FEMALE, OTHER]
            required: [first_name, last_name, birth_date, identity_number, identity_type, gender]
    responses:
      201:
        description: Usuario creado exitosamente
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                user_id:
                  type: integer
      400:
        description: Error en los datos enviados
    """
    try:
        data = request.json_body
        db = SessionLocal()
        
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
    """
    Obtener usuario actual
    ---
    tags:
      - Usuarios
    summary: Obtener usuario
    description: Obtiene los datos del usuario autenticado
    parameters:
      - in: header
        name: Authorization
        schema:
          type: string
        required: true
        description: "Bearer token"
    responses:
      200:
        description: Datos del usuario
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                first_name:
                  type: string
                last_name:
                  type: string
                birth_date:
                  type: string
                  format: date
                identity_number:
                  type: string
                identity_type:
                  type: string
                gender:
                  type: string
      401:
        description: Token requerido o inválido
      404:
        description: Usuario no encontrado
    """
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
    """
    Listar todos los usuarios
    ---
    tags:
      - Usuarios
    summary: Listar usuarios
    description: Obtiene la lista de todos los usuarios
    parameters:
      - in: header
        name: Authorization
        schema:
          type: string
        required: true
        description: "Bearer token"
    responses:
      200:
        description: Lista de usuarios
        content:
          application/json:
            schema:
              type: object
              properties:
                users:
                  type: array
                  items:
                    type: object
      401:
        description: Token requerido o inválido
    """
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
    """
    Actualizar usuario
    ---
    tags:
      - Usuarios
    summary: Actualizar usuario
    description: Actualiza los datos del usuario autenticado
    parameters:
      - in: header
        name: Authorization
        schema:
          type: string
        required: true
        description: "Bearer token"
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              first_name:
                type: string
              last_name:
                type: string
              birth_date:
                type: string
                format: date
              gender:
                type: string
                enum: [MALE, FEMALE, OTHER]
    responses:
      200:
        description: Usuario actualizado exitosamente
      401:
        description: Token requerido o inválido
      404:
        description: Usuario no encontrado
    """
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
    """
    Eliminar usuario
    ---
    tags:
      - Usuarios
    summary: Eliminar usuario
    description: Elimina el usuario autenticado
    parameters:
      - in: header
        name: Authorization
        schema:
          type: string
        required: true
        description: "Bearer token"
    responses:
      200:
        description: Usuario eliminado exitosamente
      401:
        description: Token requerido o inválido
      404:
        description: Usuario no encontrado
    """
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