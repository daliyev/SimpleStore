from django.db import models
from common.models import BaseModel
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    class Meta:
        indexes = [
            models.Index(fields=['created_at'])
        ]
        ordering = ['created_at']

    def __str__(self):
        return f'{self.name} {str(self.price)}'


class Review(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    content = models.TextField()
    rating = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f'{self.user} {self.product} {self.rating} {self.content}'
