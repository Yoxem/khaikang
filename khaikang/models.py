from django.db import models
from django.contrib.auth.models import AbstractBaseUser

class User(AbstractBaseUser):
    """customized user field."""
    username = models.CharField(max_length=30, unique=True) # max to 30 char
    USERNAME_FIELD = 'username' # setting username field to "id"

    created_time = models.DateTimeField()
    shown_name = models.CharField(max_length=50) # max to 50 char

    url = models.URLField(max_length=200) # max to 200 char


    desc = models.TextField() # description

    GROUP_CLASSES = [
    ('admin', 'admin'),
    ('sysop', 'sysop'),
    ('general', 'general'),
    ('suspended', 'suspended'),
    ('deleted', 'deleted'),
    ]

    classfication = models.CharField(
        max_length=9,
        choices=GROUP_CLASSES,
        default='general',
    )

    email = models.EmailField(max_length=200) # max to 200 char

    REQUIRED_FIELDS = ['id', 'shown_name', 'classfication', 'email']

class Following(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    followee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followee")


class Post(models.Model):
    text = models.TextField()
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    post_time = models.DateTimeField()

    GROUP_PRIVILAGES = [
    ('public', 'public'), # post to public timeline
    ('unpublic', 'unpublic'), # not post to public timeline
    ('private', 'private'), # to followers
    ]

    privilage = models.CharField(
        max_length=8,
        choices=GROUP_PRIVILAGES,
        default='public',
    )

