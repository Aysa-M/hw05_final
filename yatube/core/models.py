from django.db import models


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""
    created = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True)

    class Meta:
        """
        Внутренний класс Meta для хранения метаданных
        абстрактного класса CreateModel.
        """
        abstract = True
