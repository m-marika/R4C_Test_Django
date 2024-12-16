"""
Signals for available robots
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from orders.models import Order
from .models import Robot

@receiver(post_save, sender=Robot)
def notify_customer_when_robot_available(sender, instance, created, **kwargs): # pylint: disable=unused-argument
    """
    Handle the post_save signal to send an email notification to the
    customer when a robot becomes available
    """
    # Проверяем, стал ли робот доступным
    if instance.is_available:
        orders = Order.objects.filter(robot_serial=instance.serial) # pylint: disable=no-member
        for order in orders:
            customer_email = order.customer.email
            send_mail(
                subject="Ваш робот теперь доступен",
                message=(
                    f"Добрый день!\n"
                    f"Недавно вы интересовались нашим роботом модели {instance.model}, версии {instance.version}. " #pylint: disable=line-too-long
                    f"Этот робот теперь в наличии. Если вам подходит этот вариант - пожалуйста, свяжитесь с нами."
                ),
                from_email="no-reply@robots.com",
                recipient_list=[customer_email],
            )
