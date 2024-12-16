"""
Tests for Robot API
"""
from datetime import datetime, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from .models import Robot


class RobotAPITestCase(TestCase): # pylint: disable=too-many-public-methods
    """
    Tests for Robot API
    """

    def setUp(self):
        self.client = Client()

        # Test robot data
        self.valid_robot_data = {
            'model': 'Q1',
            'version': 'V1',
            'created': '2024-12-14 12:00:00',
        }
        # Wrong data
        self.invalid_robot_data = {
            'model': 'InvalidModel123',
            'version': 'V123', 
            'created': 'InvalidDate',
        }

        # url
        self.robot_create_url = reverse('robot-create')  # POST
        self.robot_list_url = reverse('robot-list')  # GET

        # Create test robot
        self.robot = Robot.objects.create( # pylint: disable=no-member
            serial='00001',
            model='T1',
            version='V1',
            created=datetime.now() - timedelta(days=1)
        )

    def test_create_robot_valid_data(self):
        """Test case for creating a robot with valid data"""
        response = self.client.post(
            self.robot_create_url,
            data=self.valid_robot_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('robot_id', response.json())
        self.assertEqual(Robot.objects.count(), 2)  # pylint: disable=no-member

    def test_create_robot_invalid_data(self):
        """Test that creating a robot with invalid data fails"""
        response = self.client.post(
            self.robot_create_url,
            data=self.invalid_robot_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertEqual(Robot.objects.count(), 1)  # pylint: disable=no-member

    def test_list_robots(self):
        """Test that a list of robots can be retrieved"""
        response = self.client.get(self.robot_list_url)
        self.assertEqual(response.status_code, 200)
        data = response.json().get('robots', [])
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0]['serial'], '00001')