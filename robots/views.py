import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.shortcuts import render
from django.db.models import Count
from datetime import datetime, timedelta
from openpyxl import Workbook
from .models import Robot

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

def export_robots_summary(request):
    if request.method == "GET":
        try:
            # Получаем текущую дату и дату неделю назад
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)

            # Выбираем роботов, созданных за последнюю неделю
            robots = Robot.objects.filter(created__range=(start_date, end_date))

            # Сгруппировать данные по модели и версии, подсчитать количество
            summary = robots.values('model', 'version').annotate(count=Count('id'))

            # Создаем новый Excel-файл
            wb = Workbook()
            models = set(item['model'] for item in summary)
            
            for model in models:
                # Создаем лист для каждой модели
                ws = wb.create_sheet(title=model)
                ws.append(['Модель', 'Версия', 'Количество за неделю'])

                # Добавляем строки с данными
                for item in summary:
                    if item['model'] == model:
                        ws.append([item['model'], item['version'], item['count']])
            
            # Удаляем пустой лист, созданный по умолчанию
            if "Sheet" in wb.sheetnames:
                wb.remove(wb["Sheet"])

            # Создаем HTTP-ответ с Excel-файлом
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="robots_summary.xlsx"'
            wb.save(response)

            return response

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only GET method is allowed'}, status=405)