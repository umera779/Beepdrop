
from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.conf import settings

class ReferralCode(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='referral_code')
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            # Generate a unique referral code
            self.code = get_random_string(12)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s referral code: {self.code}"

class Referral(models.Model):
    referrer = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='referrals_made')
    referred_user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='referred_by')
    created_at = models.DateTimeField(auto_now_add=True)
    reward_claimed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('referrer', 'referred_user')

    def __str__(self):
        return f"{self.referrer.username} referred {self.referred_user.username}"




# Counter model that links to the User
class Counter(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name="counter")
    value = models.PositiveBigIntegerField(default=0)    

    def __str__(self):
        return f"BALANCE: {self.value} \t \t USER={self.user}"




# TaskList model that links to the User
class TaskList(models.Model):
    Taskname = models.CharField(max_length=100)
    Taskvalue = models.PositiveIntegerField(default=0)
    link = models.URLField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    assigned_users = models.ManyToManyField('CustomUser', related_name="tasks")

    def __str__(self):
        return f"Task: {self.Taskname} - Value: {self.Taskvalue}"
# models.py


class ButtonState(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="button_state")
    state = models.CharField(max_length=10, choices=[('clicked', 'Clicked'), ('unclicked', 'Unclicked')], default='unclicked')
    last_clicked = models.DateTimeField(null=True, blank=True)  # When the button was last clicked

    def get_remaining_time(self):
        """
        Calculate the remaining time in milliseconds.
        """
        if self.last_clicked:
            elapsed_time = now() - self.last_clicked
            disable_duration = 4 * 60 * 60  # 4 hours in seconds
            remaining_time = disable_duration - elapsed_time.total_seconds()
            return max(0, remaining_time * 1000)  # Return in milliseconds
        return 0


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email)
        user.set_password(password)
        user.save(using=self._db)
        user.is_active = False  # User will be inactive until email is verified

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

    # def _create_user_related_fields(self, user):
    #     # Create related models for Counter, Level, Mining, TaskList, and Boost
    #     Counter.objects.create(user=user)
    #     Mining.objects.create(user=user)
    #     Boost.objects.create(user=user)
    #     TaskList.objects.create(user=user)
    #     Level.objects.create(user=user)

    def _create_user_related_fields(self, user):
    # Create related models for Counter, Level, Mining
        Counter.objects.create(user=user)
        Mining.objects.create(user=user)
        Level.objects.create(user=user)


        task = TaskList.objects.create(
            Taskname="Default Task",
            Taskvalue=1000
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

