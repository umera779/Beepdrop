
from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.conf import settings

from django.conf import settings
from django.db import models

class Referral(models.Model):
    referrer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='referrals_given',
        on_delete=models.CASCADE
    )
    referred_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='referral_received',
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.referrer.username} referred {self.referred_user.username}"


class ReferralCode(models.Model):
    referrer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='referral_codes',
        on_delete=models.CASCADE
    )
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Referral code {self.code} for {self.referrer.username}"



# Counter model that links to the User
class Counter(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name="counter")
    value = models.PositiveBigIntegerField(default=2000)    

    def __str__(self):
        return f"BALANCE: {self.value} \t \t USER={self.user}"




# TaskList model that links to the User
class TaskList(models.Model):
    Taskname = models.CharField(max_length=100,blank=True, null=True)
    Taskvalue = models.PositiveIntegerField(default=0,blank=True, null=True)
    link = models.URLField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    assigned_users = models.ManyToManyField('CustomUser', related_name="tasks")

    def __str__(self):
        return f"Task: {self.Taskname} - Value: {self.Taskvalue}"
# models.py





class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email)
        user.set_password(password)
        user.save(using=self._db)
        user.is_active = False # User will be inactive until email is verified change to True to create superuser

        # Create related models after user creation
        self._create_user_related_fields(user)

        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(username, email, password)
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


    def _create_user_related_fields(self, user):
    # Create related models for Counter, Level, Mining
        Counter.objects.create(user=user)
        
        task = TaskList.objects.create(
            Taskname = "Daily Bonus Task",
            Taskvalue = 100,
            link = "https://x.com", #replace this with correct social handle
            description = "Bonus Task",
        )
        task.assigned_users.add(user)

# Custom User model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    # is_active = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)  # Set to True after email verification
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Fields required for creating a superuser

    objects = CustomUserManager()

    def __str__(self):
        return self.username
    
    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Send an email to this user.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

        

## invite logic 

