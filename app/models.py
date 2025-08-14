from django.db import models


# Create your models here.
class User(models.Model):
    name = models.TextField()
    email = models.EmailField(unique=True)
    password = models.CharField(
        max_length=128, default="changeme123"
    )  # Valor por defecto temporal

    def __str__(self):
        return self.name


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    entry_time = models.DateTimeField()
    exit_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.name} - {self.entry_time}"
