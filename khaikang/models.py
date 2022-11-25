from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.utils import timezone
import hashlib





class User(AbstractUser):
    """customized user field."""
    username = models.CharField(max_length=30, unique=True) # max to 30 char
    USERNAME_FIELD = 'username' # setting username field to "id"

    created_time = models.DateTimeField(default=timezone.now(), blank=True)
    shown_name = models.CharField(max_length=50) # max to 50 char

    url = models.URLField(max_length=200) # max to 200 char

    def upload_path(instance, orig_filename):
            
            avatar_filename = hashlib.sha256(orig_filename.encode('utf-8')).hexdigest()[:10]
            return f"img/profile/user_{instance.id}/{orig_filename}"

    avatar = models.ImageField(upload_to=upload_path)

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
    is_staff = models.BooleanField(default=False)
    is_superuser =  models.BooleanField(default=False)

    email = models.EmailField(max_length=200) # max to 200 char

    objects = UserManager() # for admin user use

    REQUIRED_FIELDS = ['shown_name', 'classfication', 'email', 'is_staff', 'is_superuser']

class Following(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    followee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followee")
    IS_DECIDED = [
    ('undecided', 'undecided'),
    ('yes', 'yes'),
    ]
    isapproved = models.CharField(
        max_length=9,
        choices=IS_DECIDED,
        default='undecided',
    )


class Post(models.Model):
    text = models.TextField()
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    post_time = models.DateTimeField(default=timezone.now())

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


