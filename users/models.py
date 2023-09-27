from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Member(models.Model):

    ROLES = (('Lab Director', 'Lab Director'),
             ('Student Researcher', 'Student Researcher'))

    role = models.CharField(max_length=200, choices=ROLES)

    image = models.ImageField(
        upload_to='images/', default='images/default_member.png')

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):

        return self.user.username + ' - ' + self.role
