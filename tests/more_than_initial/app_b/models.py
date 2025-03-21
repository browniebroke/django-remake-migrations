from __future__ import annotations

from django.db import models


class Parent(models.Model):
    first_object = models.ForeignKey("app_a.Object", on_delete=models.CASCADE)
