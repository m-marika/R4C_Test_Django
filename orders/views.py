"""
This module handles order creation for customers.

It defines an API endpoint that processes POST requests to create 
a new customer order with email and robot serial information.
"""
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from .models import Order, Customer

@csrf_exempt
def create_order(request):
    """
    Handle POST requests to create an order.

    Args:
        request (HttpRequest): The HTTP request object containing JSON payload.

    Returns:
        JsonResponse: JSON response with order details or error message.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            robot_serial = data.get("robot_serial")

            if not email or not robot_serial:
                return JsonResponse(
                    {'error': 'Both "email" and "robot_serial" fields are required.'},
                    status=400)

            with transaction.atomic():  # Используем транзакцию для целостности данных
                customer, _ = Customer.objects.get_or_create(email=email) # pylint: disable=no-member

                # Создаем заказ
                order = Order.objects.create( # pylint: disable=no-member
                    customer=customer,
                    robot_serial=robot_serial
                )

                return JsonResponse({
                    'message': 'Order created successfully',
                    'order_id': order.id,
                    'customer_email': customer.email
                }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e: # pylint: disable=broad-exception-caught
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
