from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Submission(models.Model):
    title = models.CharField(max_length=100)
    abstract = models.TextField()
    file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)
    author = models.CharField(max_length=100)


    def __str__(self):
        return self.name

class Reviewer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} -> {self.submission.title}'