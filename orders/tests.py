"""
Tests for Order API
"""
import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import Order, Customer

class CreateOrderAPITestCase(TestCase):
    """
    Tests for Create Order API
    """

    def setUp(self):
        self.client = Client()
        self.create_order_url = reverse('create_order')

        # Sample test data
        self.valid_order_data = {
            "email": "test@example.com",
            "robot_serial": "R1234"
        }

        self.invalid_order_data_missing_fields = {
            "email": "test@example.com"
            # missing "robot_serial"
        }

        self.invalid_json_data = "This is not a JSON string"

    def test_create_order_success(self):
        """
        Test that an order is created successfully with valid data.
        """
        response = self.client.post(
            self.create_order_url,
            data=json.dumps(self.valid_order_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('order_id', response.json())
        self.assertEqual(Order.objects.count(), 1) # pylint: disable=no-member
        self.assertEqual(Customer.objects.count(), 1) # pylint: disable=no-member
        order = Order.objects.first() # pylint: disable=no-member
        self.assertEqual(order.robot_serial, "R1234")
        self.assertEqual(order.customer.email, "test@example.com")

    def test_create_order_missing_fields(self):
        """
        Test that API returns error when required fields are missing.
        """
        response = self.client.post(
            self.create_order_url,
            data=json.dumps(self.invalid_order_data_missing_fields),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertEqual(Order.objects.count(), 0)  # pylint: disable=no-member

    def test_create_order_invalid_json(self):
        """
        Test that API returns error for invalid JSON format.
        """
        response = self.client.post(
            self.create_order_url,
            data=self.invalid_json_data,  # Invalid JSON
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertEqual(Order.objects.count(), 0) # pylint: disable=no-member

    def test_create_order_duplicate_customer(self):
        """
        Test that orders can be created for the same
        customer without duplication of Customer entries.
        """
        # Create initial order
        self.client.post(
            self.create_order_url,
            data=json.dumps(self.valid_order_data),
            content_type='application/json'
        )

        # Create another order with the same email
        response = self.client.post(
            self.create_order_url,
            data=json.dumps({
                "email": "test@example.com",
                "robot_serial": "R5678"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.count(), 2) # pylint: disable=no-member
        self.assertEqual(Customer.objects.count(), 1)  # pylint: disable=no-member
        self.assertIn('order_id', response.json())

    def test_create_order_invalid_http_method(self):
        """
        Test that API returns error for non-POST HTTP methods.
        """
        response = self.client.get(self.create_order_url)
        self.assertEqual(response.status_code, 405)
        self.assertIn('error', response.json())
