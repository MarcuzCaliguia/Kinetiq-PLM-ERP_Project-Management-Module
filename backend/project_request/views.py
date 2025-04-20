from django.http import JsonResponse
from django.db import connection
import json
from decimal import Decimal
import datetime

def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        {columns[i]: value for i, value in enumerate(row)}
        for row in cursor.fetchall()
    ]

def serialize_result(data):
    """Convert dates and decimals to strings for JSON serialization"""
    for item in data:
        for key, value in item.items():
            if isinstance(value, datetime.date):
                item[key] = value.isoformat()
            elif isinstance(value, Decimal):
                item[key] = float(value)
    return data

def test_view(request):
    """Simple test endpoint to verify API is working"""
    return JsonResponse({"status": "ok", "message": "API is working!"})

def project_requests(request):
    """Handle project requests list (GET) and create (POST)"""
    if request.method == 'GET':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM project_management.internal_project_request
                    ORDER BY request_date DESC
                """)
                result = dictfetchall(cursor)
                return JsonResponse(serialize_result(result), safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    elif request.method == 'POST':
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            
            # Generate a new ID (you might want to use your custom function here)
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 'PROJ-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || 
                    LPAD(COALESCE(
                        (SELECT MAX(SUBSTRING(project_request_id FROM 15)::integer) + 1 
                        FROM project_management.internal_project_request 
                        WHERE project_request_id LIKE 'PROJ-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-%'), 
                    1)::text, 3, '0')
                """)
                new_id = cursor.fetchone()[0]
            
            # Insert the new project request
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO project_management.internal_project_request (
                        project_request_id, project_name, project_description, 
                        request_date, target_starting_date, 
                        employee_id, dept_id, 
                        project_budget_request, project_budget_description
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                """, [
                    new_id,
                    data.get('project_name', ''),
                    data.get('project_description', ''),
                    data.get('request_date'),
                    data.get('target_starting_date'),
                    data.get('employee_id'),
                    data.get('dept_id'),
                    data.get('project_budget_request'),
                    data.get('project_budget_description', '')
                ])
                result = dictfetchall(cursor)
                return JsonResponse(serialize_result(result)[0], safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)

def project_request_detail(request, project_id):
    """Handle single project request (GET, PUT, DELETE)"""
    if request.method == 'GET':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM project_management.internal_project_request
                    WHERE project_request_id = %s
                """, [project_id])
                result = dictfetchall(cursor)
                if not result:
                    return JsonResponse({"error": "Project request not found"}, status=404)
                return JsonResponse(serialize_result(result)[0], safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE project_management.internal_project_request
                    SET project_name = %s,
                        project_description = %s,
                        request_date = %s,
                        target_starting_date = %s,
                        employee_id = %s,
                        dept_id = %s,
                        project_budget_request = %s,
                        project_budget_description = %s
                    WHERE project_request_id = %s
                    RETURNING *
                """, [
                    data.get('project_name', ''),
                    data.get('project_description', ''),
                    data.get('request_date'),
                    data.get('target_starting_date'),
                    data.get('employee_id'),
                    data.get('dept_id'),
                    data.get('project_budget_request'),
                    data.get('project_budget_description', ''),
                    project_id
                ])
                result = dictfetchall(cursor)
                if not result:
                    return JsonResponse({"error": "Project request not found"}, status=404)
                return JsonResponse(serialize_result(result)[0], safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    elif request.method == 'DELETE':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM project_management.internal_project_request
                    WHERE project_request_id = %s
                    RETURNING project_request_id
                """, [project_id])
                result = cursor.fetchone()
                if not result:
                    return JsonResponse({"error": "Project request not found"}, status=404)
                return JsonResponse({"success": True, "deleted_id": result[0]})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)

def search_employees(request):
    """Search for employees"""
    query = request.GET.get('query', '')
    if not query:
        return JsonResponse([], safe=False)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT employee_id, first_name, last_name 
                FROM human_resources.employees
                WHERE employee_id ILIKE %s OR first_name ILIKE %s OR last_name ILIKE %s
                LIMIT 10
            """, [f'%{query}%', f'%{query}%', f'%{query}%'])
            result = dictfetchall(cursor)
            return JsonResponse(result, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def search_departments(request):
    """Search for departments"""
    query = request.GET.get('query', '')
    if not query:
        return JsonResponse([], safe=False)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT dept_id, dept_name 
                FROM human_resources.departments
                WHERE dept_id ILIKE %s OR dept_name ILIKE %s
                LIMIT 10
            """, [f'%{query}%', f'%{query}%'])
            result = dictfetchall(cursor)
            return JsonResponse(result, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)