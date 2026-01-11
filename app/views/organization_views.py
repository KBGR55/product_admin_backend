from pyramid.view import view_config
from pyramid.response import Response
import json
from app.database import SessionLocal
from app.models.user import User
from app.models.organization import Organization, OrganizationRole, OrganizationEmployee
from app.middleware.jwt_middleware import extract_token, verify_token

@view_config(route_name='create_org', renderer='json')
def create_org(request):
    try:
        token = extract_token(request)
        if not token:
            return Response(json.dumps({'error': 'Token requerido'}), status=401)
        
        payload = verify_token(token)
        user_id = payload.get('user_id')
        
        data = request.json_body
        db = SessionLocal()
        
        org_exists = db.query(Organization).filter(Organization.email == data['email']).first()
        if org_exists:
            db.close()
            return Response(json.dumps({'error': 'El correo de organización ya existe'}), status=400)
        
        new_org = Organization(
            name=data['name'],
            email=data['email'],
            legal_name=data['legal_name'],
            org_type=data['org_type'],
            description=data.get('description'),
            owner_id=user_id,
            photo_url=data.get('photo_url'),
            primary_color=data.get('primary_color', '#000000'),
            secondary_color=data.get('secondary_color', '#FFFFFF'),
            tertiary_color=data.get('tertiary_color', '#F0F0F0'),
            employee_count=data.get('employee_count', 0),
            address=data.get('address')
        )
        
        db.add(new_org)
        db.flush()  # Flush para obtener el ID
        
        # Get owner and add as member
        owner = db.query(User).filter(User.id == user_id).first()
        if owner:
            new_org.members.append(owner)
        
        db.commit()
        db.refresh(new_org)
        db.close()
        
        return {
            'message': 'Organización creada exitosamente',
            'organization_id': new_org.id,
            'name': new_org.name
        }
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)

@view_config(route_name='get_org', renderer='json')
def get_org(request):
    try:
        token = extract_token(request)
        if not token:
            return Response(json.dumps({'error': 'Token requerido'}), status=401)
        
        verify_token(token)
        
        org_id = request.matchdict.get('org_id')
        db = SessionLocal()
        
        org = db.query(Organization).filter(Organization.id == org_id).first()
        db.close()
        
        if not org:
            return Response(json.dumps({'error': 'Organización no encontrada'}), status=404)
        
        return {
            'id': org.id,
            'name': org.name,
            'email': org.email,
            'legal_name': org.legal_name,
            'org_type': org.org_type,
            'description': org.description,
            'owner_id': org.owner_id,
            'photo_url': org.photo_url,
            'primary_color': org.primary_color,
            'secondary_color': org.secondary_color,
            'tertiary_color': org.tertiary_color,
            'employee_count': org.employee_count,
            'address': org.address,
            'created_at': str(org.created_at)
        }
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)

@view_config(route_name='list_org', renderer='json')
def list_org(request):
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
        
        organizations = user.organizations
        db.close()
        
        return {
            'organizations': [
                {
                    'id': org.id,
                    'name': org.name,
                    'email': org.email,
                    'legal_name': org.legal_name,
                    'org_type': org.org_type,
                    'description': org.description,
                    'primary_color': org.primary_color,
                    'secondary_color': org.secondary_color,
                    'tertiary_color': org.tertiary_color,
                    'employee_count': org.employee_count,
                    'created_at': str(org.created_at)
                }
                for org in organizations
            ]
        }
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)

@view_config(route_name='update_org', renderer='json')
def update_org(request):
    try:
        token = extract_token(request)
        if not token:
            return Response(json.dumps({'error': 'Token requerido'}), status=401)
        
        payload = verify_token(token)
        user_id = payload.get('user_id')
        
        org_id = request.matchdict.get('org_id')
        data = request.json_body
        
        db = SessionLocal()
        
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            db.close()
            return Response(json.dumps({'error': 'Organización no encontrada'}), status=404)
        
        if org.owner_id != user_id:
            db.close()
            return Response(json.dumps({'error': 'No tienes permiso para actualizar esta organización'}), status=403)
        
        org.name = data.get('name', org.name)
        org.legal_name = data.get('legal_name', org.legal_name)
        org.org_type = data.get('org_type', org.org_type)
        org.description = data.get('description', org.description)
        org.photo_url = data.get('photo_url', org.photo_url)
        org.primary_color = data.get('primary_color', org.primary_color)
        org.secondary_color = data.get('secondary_color', org.secondary_color)
        org.tertiary_color = data.get('tertiary_color', org.tertiary_color)
        org.employee_count = data.get('employee_count', org.employee_count)
        org.address = data.get('address', org.address)
        
        db.commit()
        db.close()
        
        return {'message': 'Organización actualizada exitosamente'}
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)

@view_config(route_name='delete_org', renderer='json')
def delete_org(request):
    try:
        token = extract_token(request)
        if not token:
            return Response(json.dumps({'error': 'Token requerido'}), status=401)
        
        payload = verify_token(token)
        user_id = payload.get('user_id')
        
        org_id = request.matchdict.get('org_id')
        db = SessionLocal()
        
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            db.close()
            return Response(json.dumps({'error': 'Organización no encontrada'}), status=404)
        
        if org.owner_id != user_id:
            db.close()
            return Response(json.dumps({'error': 'No tienes permiso para eliminar esta organización'}), status=403)
        
        db.delete(org)
        db.commit()
        db.close()
        
        return {'message': 'Organización eliminada exitosamente'}
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)

@view_config(route_name='add_employee', renderer='json')
def add_employee(request):
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
        
        user = db.query(User).filter(User.id == data['user_id']).first()
        if not user:
            db.close()
            return Response(json.dumps({'error': 'Usuario no encontrado'}), status=404)
        
        employee_exists = db.query(OrganizationEmployee).filter(
            OrganizationEmployee.org_id == org_id,
            OrganizationEmployee.user_id == data['user_id']
        ).first()
        
        if employee_exists:
            db.close()
            return Response(json.dumps({'error': 'El usuario ya es empleado de esta organización'}), status=400)
        
        new_employee = OrganizationEmployee(
            org_id=org_id,
            user_id=data['user_id']
        )
        
        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)
        db.close()
        
        return {
            'message': 'Empleado agregado exitosamente',
            'employee_id': new_employee.id
        }
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)

@view_config(route_name='remove_employee', renderer='json')
def remove_employee(request):
    try:
        token = extract_token(request)
        if not token:
            return Response(json.dumps({'error': 'Token requerido'}), status=401)
        
        verify_token(token)
        
        org_id = request.matchdict.get('org_id')
        user_id = request.matchdict.get('user_id')
        
        db = SessionLocal()
        
        employee = db.query(OrganizationEmployee).filter(
            OrganizationEmployee.org_id == org_id,
            OrganizationEmployee.user_id == user_id
        ).first()
        
        if not employee:
            db.close()
            return Response(json.dumps({'error': 'Empleado no encontrado'}), status=404)
        
        db.delete(employee)
        db.commit()
        db.close()
        
        return {'message': 'Empleado removido exitosamente'}
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)

@view_config(route_name='list_employees', renderer='json')
def list_employees(request):
    try:
        token = extract_token(request)
        if not token:
            return Response(json.dumps({'error': 'Token requerido'}), status=401)
        
        verify_token(token)
        
        org_id = request.matchdict.get('org_id')
        db = SessionLocal()
        
        employees = db.query(OrganizationEmployee).filter(
            OrganizationEmployee.org_id == org_id
        ).all()
        
        db.close()
        
        return {
            'employees': [
                {
                    'id': emp.id,
                    'user_id': emp.user_id,
                    'first_name': emp.user.first_name,
                    'last_name': emp.user.last_name,
                    'email': emp.user.account.email if emp.user.account else None,
                    'roles': [role.name for role in emp.roles],
                    'created_at': str(emp.created_at)
                }
                for emp in employees
            ]
        }
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)

@view_config(route_name='create_org_role', renderer='json')
def create_org_role(request):
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
        
        role_exists = db.query(OrganizationRole).filter(
            OrganizationRole.org_id == org_id,
            OrganizationRole.name == data['name']
        ).first()
        
        if role_exists:
            db.close()
            return Response(json.dumps({'error': 'El rol ya existe en esta organización'}), status=400)
        
        new_role = OrganizationRole(
            org_id=org_id,
            name=data['name'],
            description=data.get('description', '')
        )
        
        db.add(new_role)
        db.commit()
        db.refresh(new_role)
        db.close()
        
        return {
            'message': 'Rol de organización creado exitosamente',
            'role_id': new_role.id,
            'name': new_role.name
        }
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)

@view_config(route_name='list_org_roles', renderer='json')
def list_org_roles(request):
    try:
        token = extract_token(request)
        if not token:
            return Response(json.dumps({'error': 'Token requerido'}), status=401)
        
        verify_token(token)
        
        org_id = request.matchdict.get('org_id')
        db = SessionLocal()
        
        roles = db.query(OrganizationRole).filter(OrganizationRole.org_id == org_id).all()
        db.close()
        
        return {
            'roles': [
                {
                    'id': role.id,
                    'name': role.name,
                    'description': role.description
                }
                for role in roles
            ]
        }
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)

@view_config(route_name='assign_org_role', renderer='json')
def assign_org_role(request):
    try:
        token = extract_token(request)
        if not token:
            return Response(json.dumps({'error': 'Token requerido'}), status=401)
        
        verify_token(token)
        
        org_id = request.matchdict.get('org_id')
        employee_id = request.matchdict.get('employee_id')
        role_id = request.matchdict.get('role_id')
        
        db = SessionLocal()
        
        employee = db.query(OrganizationEmployee).filter(
            OrganizationEmployee.id == employee_id,
            OrganizationEmployee.org_id == org_id
        ).first()
        
        if not employee:
            db.close()
            return Response(json.dumps({'error': 'Empleado no encontrado'}), status=404)
        
        role = db.query(OrganizationRole).filter(
            OrganizationRole.id == role_id,
            OrganizationRole.org_id == org_id
        ).first()
        
        if not role:
            db.close()
            return Response(json.dumps({'error': 'Rol no encontrado'}), status=404)
        
        if role in employee.roles:
            db.close()
            return Response(json.dumps({'error': 'El empleado ya tiene este rol'}), status=400)
        
        employee.roles.append(role)
        db.commit()
        db.close()
        
        return {'message': 'Rol asignado exitosamente al empleado'}
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)

@view_config(route_name='remove_org_role', renderer='json')
def remove_org_role(request):
    try:
        token = extract_token(request)
        if not token:
            return Response(json.dumps({'error': 'Token requerido'}), status=401)
        
        verify_token(token)
        
        org_id = request.matchdict.get('org_id')
        employee_id = request.matchdict.get('employee_id')
        role_id = request.matchdict.get('role_id')
        
        db = SessionLocal()
        
        employee = db.query(OrganizationEmployee).filter(
            OrganizationEmployee.id == employee_id,
            OrganizationEmployee.org_id == org_id
        ).first()
        
        if not employee:
            db.close()
            return Response(json.dumps({'error': 'Empleado no encontrado'}), status=404)
        
        role = db.query(OrganizationRole).filter(
            OrganizationRole.id == role_id,
            OrganizationRole.org_id == org_id
        ).first()
        
        if not role:
            db.close()
            return Response(json.dumps({'error': 'Rol no encontrado'}), status=404)
        
        if role not in employee.roles:
            db.close()
            return Response(json.dumps({'error': 'El empleado no tiene este rol'}), status=400)
        
        employee.roles.remove(role)
        db.commit()
        db.close()
        
        return {'message': 'Rol removido exitosamente del empleado'}
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400)