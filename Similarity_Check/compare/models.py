from django.db import models

class Book(models.Model):
    book_id = models.BigAutoField(primary_key=True)  # New auto-incremented primary key
    book_title = models.CharField(max_length=255)
    authors = models.CharField(max_length=255)
    area = models.CharField(max_length=100)
    year = models.IntegerField()
    file = models.FileField(upload_to='books/', null=True, blank=True)  # To attach the book file

    def __str__(self):
        return self.book_title
