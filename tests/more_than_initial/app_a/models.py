from __future__ import annotations

from django.db import models


class Object(models.Model):
    fk = models.ForeignKey(
        "app_b.Parent",
        on_delete=models.CASCADE,
    )
