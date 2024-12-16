"""
Model for Robot
"""
from django.db import models


class Robot(models.Model):
    """
    Represents a customer order.
    Attributes:
        serial (str): The serial number of the robot.
        model (str): The model of the robot.
        version (str): The version of the robot.
        created (datetime): The date and time the robot was created.
        is_available (bool): Whether the robot is available for purchase.
    """
    serial = models.CharField(max_length=5, blank=False, null=False)
    model = models.CharField(max_length=2, blank=False, null=False)
    version = models.CharField(max_length=2, blank=False, null=False)
    created = models.DateTimeField(blank=False, null=False)
    is_available = models.BooleanField(default=False)
