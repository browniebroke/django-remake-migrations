from __future__ import annotations

from django.db import models


class Book(models.Model):
    fk = models.ForeignKey(
        "app2.Author",
        on_delete=models.CASCADE,
    )
