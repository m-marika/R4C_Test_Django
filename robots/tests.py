from django.test import TestCase, Client
from django.urls import reverse
from .models import Robot
from datetime import datetime

class RobotAPITestCase(TestCase):
    def setUp(self):
        # Настройка тестового клиента
        self.client = Client()

        # Тестовые данные для POST-запроса
        self.valid_robot_data = {
            'model': 'R1',
            'version': 'V1',
            'created': '2024-12-14 12:00:00'
        }
        self.invalid_robot_data = {
            'model': 'InvalidModel123',  # Невалидная длина
            'version': 'V123',          # Невалидная длина
            'created': 'InvalidDate'    # Невалидный формат даты
        }

        # URL-адреса
        self.robot_create_url = reverse('robot-create')
        self.robot_list_url = reverse('robot-list')

    def test_create_robot_success(self):
        # Тест на успешное создание робота
        response = self.client.post(
            self.robot_create_url, 
            data=self.valid_robot_data, 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.json())
        self.assertIn('robot_id', response.json())

        # Проверяем, что робот был создан в базе данных
        robot = Robot.objects.get(id=response.json()['robot_id'])
        self.assertEqual(robot.model, self.valid_robot_data['model'])
        self.assertEqual(robot.version, self.valid_robot_data['version'])
        self.assertEqual(robot.created, datetime.strptime(self.valid_robot_data['created'], '%Y-%m-%d %H:%M:%S'))

    def test_create_robot_missing_field(self):
        # Тест на отсутствие обязательных полей
        incomplete_data = self.valid_robot_data.copy()
        incomplete_data.pop('model')  # Убираем поле "model"
        response = self.client.post(
            self.robot_create_url, 
            data=incomplete_data, 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertEqual(response.json()['error'], 'Missing field: model')

    def test_create_robot_invalid_data(self):
        # Тест на отправку невалидных данных
        response = self.client.post(
            self.robot_create_url, 
            data=self.invalid_robot_data, 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_create_robot_invalid_json(self):
        # Тест на отправку невалидного JSON
        response = self.client.post(
            self.robot_create_url, 
            data="Invalid JSON",
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertEqual(response.json()['error'], 'Invalid JSON')

    def test_get_robot_list(self):
        # Тест на получение списка всех роботов
        # Создаем несколько записей роботов
        Robot.objects.create(serial="00001", model="R1", version="V1", created=datetime.now())
        Robot.objects.create(serial="00002", model="R2", version="V2", created=datetime.now())

        # Выполняем GET-запрос
        response = self.client.get(self.robot_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('robots', response.json())
        self.assertEqual(len(response.json()['robots']), 2)

    def test_get_robot_list_empty(self):
        # Тест на получение пустого списка роботов
        response = self.client.get(self.robot_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('robots', response.json())
        self.assertEqual(len(response.json()['robots']), 0)

    def test_robot_list_only_get_allowed(self):
        # Тест на недопустимость других методов, кроме GET
        response = self.client.post(self.robot_list_url, data={}, content_type='application/json')
        self.assertEqual(response.status_code, 405)
        self.assertIn('error', response.json())
        self.assertEqual(response.json()['error'], 'Only GET method is allowed')
