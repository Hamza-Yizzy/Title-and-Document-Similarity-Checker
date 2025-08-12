from django.db import models
from django.contrib.auth.models import User

class Book(models.Model):
    book_id = models.BigAutoField(primary_key=True)
    book_title = models.CharField(max_length=255)
    authors = models.CharField(max_length=255)
    area = models.CharField(max_length=100)
    year = models.IntegerField()
    file = models.FileField(upload_to='books/', null=True, blank=True)

    def __str__(self):
        return self.book_title

class ComparisonHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    compared_with = models.ForeignKey(Book, on_delete=models.CASCADE, null=True)
    similarity_score = models.FloatField()
    uploaded_title = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.similarity_score:.2f}"
