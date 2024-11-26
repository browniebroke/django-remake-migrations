from __future__ import annotations

from django.contrib.postgres.indexes import GinIndex, OpClass
from django.db import models
from django.db.models.functions import Upper


class Artist(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            GinIndex(
                fields=["name"],
                name="artist_name_gin_idx",
                opclasses=["gin_trgm_ops"],
            ),
            GinIndex(
                OpClass(Upper("name"), "gin_trgm_ops"),
                name="artist_name_upper_gin_idx",
            ),
        ]
