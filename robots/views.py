import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Robot
from django.utils.dateparse import parse_datetime
from django.shortcuts import render

def create_robot_web(request):
    return render(request, 'create_robot.html')

@csrf_exempt
def robot_create_view(request):
    if request.method == "POST":
        try:
            # Разбор JSON-данных
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
            
            # Сохранение в базу данных
            robot = Robot.objects.create(
                serial=str(Robot.objects.count() + 1).zfill(5),  # Генерация серийного номера
                model=model,
                version=version,
                created=created
            )
            return JsonResponse({'message': 'Robot created successfully', 'robot_id': robot.id}, status=201)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

def robot_list_view(request):
    if request.method == "GET":
        try:
            # Получение всех записей роботов из базы данных
            robots = Robot.objects.all()

            # Преобразование в список словарей
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

            # Возвращаем JSON с данными
            return JsonResponse({'robots': robot_list}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only GET method is allowed'}, status=405)
