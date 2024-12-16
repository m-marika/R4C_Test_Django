"""
Views for robots
"""
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.shortcuts import render
from .models import Robot

def create_robot_web(request):
    """
    Render form for creating a robot
    """
    return render(request, 'create_robot.html')

@csrf_exempt
def robot_create_view(request):
    """
    Handle POST requests to create a robot.

    Args:
    request (HttpRequest): The HTTP request containing JSON data.
    Returns:
    JsonResponse: A JSON response indicating the result of the operation.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            # Валидация обязательных полей
            required_fields = ['model', 'version', 'created']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing field: {field}'}, status=400)
            
            # Дополнительная валидация
            model = data['model']
            version = data['version']
            created = parse_datetime(data['created'])
            
            if not created:
                return JsonResponse({'error': 'Invalid date format for "created". Use YYYY-MM-DD HH:MM:SS.'}, status=400)
            
            if not model.isalnum() or len(model) > 2:
                return JsonResponse({'error': 'Invalid "model". It must be alphanumeric and at most 2 characters.'}, status=400)
            
            if len(version) > 2:
                return JsonResponse({'error': 'Invalid "version". It must be at most 2 characters.'}, status=400)
            
            robot = Robot.objects.create( # pylint: disable=no-member
                serial=str(Robot.objects.count() + 1).zfill(5),  # pylint: disable=no-member
                model=model,
                version=version,
                created=created
            )
            return JsonResponse({'message': 'Robot created successfully', 'robot_id': robot.id}, status=201)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e: # pylint: disable=broad-except
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

def robot_list_view(request):
    """
    Handle GET requests to retrieve a list of robots.

    Args:
    request (HttpRequest): The HTTP request object.

    Returns:
    JsonResponse: A JSON response containing a list of robots.
    """
    if request.method == "GET":
        try:
            robots = Robot.objects.all() # pylint: disable=no-member

            robot_list = [
                {
                    'id': robot.id,
                    'serial': robot.serial,
                    'model': robot.model,
                    'version': robot.version,
                    'created': robot.created.strftime('%Y-%m-%d %H:%M:%S')
                }
                for robot in robots
            ]

            return JsonResponse({'robots': robot_list}, status=200)

        except Exception as e: # pylint: disable=broad-except
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only GET method is allowed'}, status=405)