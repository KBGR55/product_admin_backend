from pyramid.view import view_config
from pyramid.response import Response
import json
from app.database import SessionLocal
from app.models.user import User
from app.models.account import Account
from app.models.organization import Organization, OrganizationRole, OrganizationEmployee
from app.middleware.jwt_middleware import extract_token, verify_token
from sqlalchemy.orm import joinedload

def get_current_user_id(request):
    """Extrae y valida el token, retorna el user_id"""
    token = extract_token(request)
    if not token:
        return None, Response(json_body({'error': 'Token requerido'}), status=401)
    
    try:
        payload = verify_token(token)
        return payload.get('user_id'), None
    except Exception as e:
        return None, Response(json_body({'error': str(e)}), status=400)

@view_config(route_name='create_org', renderer='json')
def create_org(request):
    user_id, error = get_current_user_id(request)
    if error:
        return error

    db = SessionLocal()
    try:
        data = request.json_body

        # Validar email único
        if db.query(Organization).filter(Organization.email == data['email']).first():
            return Response(
                json_body({'error': 'El correo de organización ya existe'}),
                status=400,
                content_type='application/json'
            )

        new_org = Organization(
            name=data['name'],
            email=data['email'],
            legal_name=data['legal_name'],
            org_type=data['org_type'],
            description=data.get('description'),
            code_telephone=data.get('code_telephone'),
            telephone=data.get('telephone'),
            owner_id=user_id,
            primary_color=data.get('primary_color', '#000000'),
            secondary_color=data.get('secondary_color', '#FFFFFF'),
            tertiary_color=data.get('tertiary_color', '#F0F0F0'),
            employee_count=1,
            address=data.get('address'),
            extra_data=data.get('extra_data', {})
        )

        db.add(new_org)
        db.flush()  # obtiene new_org.id

        new_employee = OrganizationEmployee(
            org_id=new_org.id,
            user_id=user_id
        )
        db.add(new_employee)

        db.commit()
        db.refresh(new_org)

        return {
            'message': 'Organización creada exitosamente',
            'organization_id': new_org.id,
            'name': new_org.name
        }

    except KeyError as e:
        db.rollback()
        return Response(
            json_body({'error': f'Campo requerido faltante: {str(e)}'}),
            status=400,
            content_type='application/json'
        )

    except Exception as e:
        db.rollback()
        return Response(
            json_body({'error': str(e)}),
            status=500,
            content_type='application/json'
        )

    finally:
        db.close()  

@view_config(route_name='get_org', renderer='json')
def get_org(request):
    user_id, error = get_current_user_id(request)
    if error:
        return error

    db = SessionLocal()
    try:
        org_id = request.matchdict.get('org_id')

        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            return Response(
                json_body({'error': 'Organización no encontrada'}),
                status=404,
                content_type='application/json'
            )

        return {
            'id': org.id,
            'name': org.name,
            'email': org.email,
            'legal_name': org.legal_name,
            'org_type': org.org_type,
            'description': org.description,
            'code_telephone': org.code_telephone,
            'telephone': org.telephone,
            'owner_id': org.owner_id,
            'primary_color': org.primary_color,
            'secondary_color': org.secondary_color,
            'tertiary_color': org.tertiary_color,
            'employee_count': org.employee_count,
            'address': org.address,
            'is_active': org.is_active,
            'extra_data': org.extra_data,
            'created_at': org.created_at.isoformat()
        }

    except Exception as e:
        db.rollback()
        return Response(
            json_body({'error': str(e)}),
            status=500,
            content_type='application/json'
        )

    finally:
        db.close()

@view_config(route_name='list_org', renderer='json')
def list_org(request):
    user_id, error = get_current_user_id(request)
    if error:
        return error

    db = SessionLocal()
    try:
        organizations = (
            db.query(Organization)
            .filter(
                (Organization.owner_id == user_id) |
                (Organization.employees.any(OrganizationEmployee.user_id == user_id))
            )
            .all()
        )

        return {
            'organizations': [
                {
                    'id': org.id,
                    'name': org.name,
                    'email': org.email,
                    'legal_name': org.legal_name,
                    'org_type': org.org_type,
                    'description': org.description,
                    'code_telephone': org.code_telephone,
                    'telephone': org.telephone,
                    'primary_color': org.primary_color,
                    'secondary_color': org.secondary_color,
                    'tertiary_color': org.tertiary_color,
                    'employee_count': org.employee_count,
                    'is_active': org.is_active,
                    'extra_data': org.extra_data,
                    'created_at': org.created_at.isoformat()
                }
                for org in organizations
            ]
        }

    except Exception as e:
        db.rollback()  
        return Response(
            json_body({'error': str(e)}),
            status=500,
            content_type='application/json'
        )

    finally:
        db.close()     

@view_config(route_name='update_org', renderer='json')
def update_org(request):
    user_id, error = get_current_user_id(request)
    if error:
        return error

    db = SessionLocal()
    try:
        org_id = request.matchdict.get('org_id')
        data = request.json_body

        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            return Response(
                json_body({'error': 'Organización no encontrada'}),
                status=404,
                content_type='application/json'
            )

        if org.owner_id != user_id:
            return Response(
                json_body({'error': 'No tienes permiso para actualizar esta organización'}),
                status=403,
                content_type='application/json'
            )

        updatable_fields = [
            'name',
            'legal_name',
            'org_type',
            'description',
            'code_telephone',
            'telephone',
            'primary_color',
            'secondary_color',
            'tertiary_color',
            'address',
            'is_active',
            'extra_data'  
        ]

        for field in updatable_fields:
            if field in data:
                setattr(org, field, data[field])

        db.commit()
        return {'message': 'Organización actualizada exitosamente'}

    except Exception as e:
        db.rollback()
        return Response(
            json_body({'error': str(e)}),
            status=500,
            content_type='application/json'
        )

    finally:
        db.close()

@view_config(route_name='delete_org', renderer='json')
def delete_org(request):
    user_id, error = get_current_user_id(request)
    if error:
        return error
    
    try:
        org_id = request.matchdict.get('org_id')
        db = SessionLocal()
        
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            db.close()
            return Response(json_body({'error': 'Organización no encontrada'}), status=404)
        
        if org.owner_id != user_id:
            db.close()
            return Response(json_body({'error': 'No tienes permiso para eliminar esta organización'}), status=403)
        
        db.delete(org)
        db.commit()
        db.close()
        
        return {'message': 'Organización eliminada exitosamente'}
    except Exception as e:
        return Response(json_body({'error': str(e)}), status=500)

@view_config(route_name='add_employee', renderer='json')
def add_employee(request):
    user_id, error = get_current_user_id(request)
    if error:
        return error
    
    try:
        org_id = request.matchdict.get('org_id')
        data = request.json_body
        
        db = SessionLocal()
        
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            db.close()
            return Response(json_body({'error': 'Organización no encontrada'}), status=404)
        
        if org.owner_id != user_id:
            db.close()
            return Response(json_body({'error': 'No tienes permiso para agregar empleados'}), status=403)
        
        new_user_id = data.get('user_id')
        user = db.query(User).filter(User.id == new_user_id).first()
        if not user:
            db.close()
            return Response(json_body({'error': 'Usuario no encontrado'}), status=404)
        
        # Verificar que el empleado no exista
        if db.query(OrganizationEmployee).filter(
            OrganizationEmployee.org_id == org_id,
            OrganizationEmployee.user_id == new_user_id
        ).first():
            db.close()
            return Response(json_body({'error': 'El usuario ya es empleado de esta organización'}), status=400)
        
        new_employee = OrganizationEmployee(
            org_id=org_id,
            user_id=new_user_id
        )
        
        org.employee_count = (org.employee_count or 0) + 1
        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)
        db.close()
        
        return {
            'message': 'Empleado agregado exitosamente',
            'employee_id': new_employee.id
        }
    except KeyError as e:
        return Response(json_body({'error': f'Campo requerido faltante: {str(e)}'}), status=400)
    except Exception as e:
        return Response(json_body({'error': str(e)}), status=500)

@view_config(route_name='remove_employee', renderer='json')
def remove_employee(request):
    user_id, error = get_current_user_id(request)
    if error:
        return error
    
    try:
        org_id = request.matchdict.get('org_id')
        employee_id = request.matchdict.get('employee_id')
        
        db = SessionLocal()
        
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            db.close()
            return Response(json_body({'error': 'Organización no encontrada'}), status=404)
        
        if org.owner_id != user_id:
            db.close()
            return Response(json_body({'error': 'No tienes permiso para remover empleados'}), status=403)
        
        employee = db.query(OrganizationEmployee).filter(
            OrganizationEmployee.id == employee_id,
            OrganizationEmployee.org_id == org_id
        ).first()
        
        if not employee:
            db.close()
            return Response(json_body({'error': 'Empleado no encontrado'}), status=404)
        
        org.employee_count = max(0, (org.employee_count or 1) - 1)
        db.delete(employee)
        db.commit()
        db.close()
        
        return {'message': 'Empleado removido exitosamente'}
    except Exception as e:
        return Response(json_body({'error': str(e)}), status=500)

@view_config(route_name='list_employees', renderer='json')
def list_employees(request):
    user_id, error = get_current_user_id(request)
    if error:
        return error

    org_id = int(request.matchdict['org_id'])
    db = SessionLocal()

    try:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            return Response(json_body({'error': 'Organización no encontrada'}), status=404)

        employees = (
            db.query(OrganizationEmployee)
            .options(
                joinedload(OrganizationEmployee.user),
                joinedload(OrganizationEmployee.roles)
            )
            .filter(
                OrganizationEmployee.org_id == org_id,
                OrganizationEmployee.is_active == True
            )
            .all()
        )

        return {
            "employees": [
                {
                    "employee_id": e.id,
                    "user_id": e.user.id if e.user else None,
                    "first_name": e.user.first_name if e.user else None,
                    "last_name": e.user.last_name if e.user else None,
                    "roles": [r.name for r in e.roles]
                }
                for e in employees
            ]
        }

    finally:
        db.close()

@view_config(route_name='create_org_role', request_method='POST', renderer='json')
def create_org_role(request):
    user_id, error = get_current_user_id(request)
    if error:
        return error

    db = SessionLocal()
    try:
        org_id = request.matchdict['org_id']
        data = request.json_body

        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org or org.owner_id != user_id:
            return {'error': 'No tienes permiso para crear roles'}

        role = OrganizationRole(
            org_id=org_id,
            name=data['name'],
            description=data.get('description')
        )

        db.add(role)
        db.commit()
        db.refresh(role)

        return {
            'id': role.id,
            'name': role.name,
            'description': role.description
        }
    finally:
        db.close()


@view_config(route_name='list_org_roles', renderer='json')
def list_org_roles(request):
    user_id, error = get_current_user_id(request)
    if error:
        return error
    
    try:
        org_id = request.matchdict.get('org_id')
        db = SessionLocal()
        
        roles = db.query(OrganizationRole).filter(OrganizationRole.org_id == org_id).all()
        db.close()
        
        return {
            'roles': [
                {
                    'id': role.id,
                    'name': role.name,
                    'description': role.description,
                    'created_at': role.created_at.isoformat()
                }
                for role in roles
            ]
        }
    except Exception as e:
        return Response(json_body({'error': str(e)}), status=500)

@view_config(route_name='assign_org_role', renderer='json')
def assign_org_role(request):
    user_id, error = get_current_user_id(request)
    if error:
        return error
    
    try:
        org_id = request.matchdict.get('org_id')
        employee_id = request.matchdict.get('employee_id')
        role_id = request.matchdict.get('role_id')
        
        db = SessionLocal()
        
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org or org.owner_id != user_id:
            db.close()
            return Response(json_body({'error': 'No tienes permiso para asignar roles'}), status=403)
        
        employee = db.query(OrganizationEmployee).filter(
            OrganizationEmployee.id == employee_id,
            OrganizationEmployee.org_id == org_id
        ).first()
        
        if not employee:
            db.close()
            return Response(json_body({'error': 'Empleado no encontrado'}), status=404)
        
        role = db.query(OrganizationRole).filter(
            OrganizationRole.id == role_id,
            OrganizationRole.org_id == org_id
        ).first()
        
        if not role:
            db.close()
            return Response(json_body({'error': 'Rol no encontrado'}), status=404)
        
        if role in employee.roles:
            db.close()
            return Response(json_body({'error': 'El empleado ya tiene este rol'}), status=400)
        
        employee.roles.append(role)
        db.commit()
        db.close()
        
        return {'message': 'Rol asignado exitosamente al empleado'}
    except Exception as e:
        return Response(json_body({'error': str(e)}), status=500)

@view_config(route_name='remove_org_role', renderer='json')
def remove_org_role(request):
    user_id, error = get_current_user_id(request)
    if error:
        return error
    
    try:
        org_id = request.matchdict.get('org_id')
        employee_id = request.matchdict.get('employee_id')
        role_id = request.matchdict.get('role_id')
        
        db = SessionLocal()
        
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org or org.owner_id != user_id:
            db.close()
            return Response(json_body({'error': 'No tienes permiso para remover roles'}), status=403)
        
        employee = db.query(OrganizationEmployee).filter(
            OrganizationEmployee.id == employee_id,
            OrganizationEmployee.org_id == org_id
        ).first()
        
        if not employee:
            db.close()
            return Response(json_body({'error': 'Empleado no encontrado'}), status=404)
        
        role = db.query(OrganizationRole).filter(
            OrganizationRole.id == role_id,
            OrganizationRole.org_id == org_id
        ).first()
        
        if not role:
            db.close()
            return Response(json_body({'error': 'Rol no encontrado'}), status=404)
        
        if role not in employee.roles:
            db.close()
            return Response(json_body({'error': 'El empleado no tiene este rol'}), status=400)
        
        employee.roles.remove(role)
        db.commit()
        db.close()
        
        return {'message': 'Rol removido exitosamente del empleado'}
    except Exception as e:
        return Response(json_body({'error': str(e)}), status=500)

@view_config(route_name='list_public_organizations', renderer='json', request_method='GET')
def list_public_organizations(request):
    """
    Lista todas las organizaciones activas sin requerir autenticación.
    Retorna solo información pública de las organizaciones.
    """
    db = SessionLocal()
    try:
        # Obtener solo organizaciones activas
        organizations = (
            db.query(Organization)
            .filter(Organization.is_active == True)
            .order_by(Organization.created_at.desc())
            .all()
        )

        return {
            'organizations': [
                {
                    'id': org.id,
                    'name': org.name,
                    'org_type': org.org_type,
                    'description': org.description,
                    'primary_color': org.primary_color,
                    'secondary_color': org.secondary_color,
                    'tertiary_color': org.tertiary_color,
                    'employee_count': org.employee_count,
                    'address': org.address,
                    'created_at': org.created_at.isoformat()
                }
                for org in organizations
            ],
            'count': len(organizations)
        }

    except Exception as e:
        db.rollback()
        return Response(
            json_body({'error': str(e)}),
            status=500,
            content_type='application/json'
        )

    finally:
        db.close()