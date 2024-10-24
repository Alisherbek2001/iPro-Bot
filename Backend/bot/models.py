from django.db import models


class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    language = models.CharField(max_length=2, choices=[('uz', 'uz'),('ru', 'ru')], default='uz')

    def __str__(self):
        return f"User {self.telegram_id} ({self.language})"