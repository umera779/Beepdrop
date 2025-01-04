
from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Counter model that links to the User
class Counter(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name="counter")
    value = models.PositiveBigIntegerField(default=0)    

    def __str__(self):
        return f"BALANCE: {self.value} \t \t USER={self.user}"

# Level model that links to the User
class Level(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name="level")
    level = models.PositiveIntegerField(null=True, blank=True, default=1)  # Default to level 1

    def __str__(self):
        return f"level: {self.level}"

# Mining model that links to the User
class Mining(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name="mining")
    speed = models.PositiveIntegerField(default=3000, blank=True, null=True)  # Default mining speed

    def __str__(self):
        return f"MINING SPEED: {self.speed} USER={self.user}"

# Boost model that links to the User
class Boost(models.Model):
    assigned_users = models.ManyToManyField('CustomUser', related_name='boost')
    boost_name = models.CharField(max_length=100, blank=True, null=True)
    boost_value = models.PositiveIntegerField(blank=True, null=True)
    needed_coin = models.PositiveIntegerField(blank=True, null=True)
    level = models.CharField(blank=True, null=True, max_length=20, unique=False)
    def __str__(self):
        return f"Boost name: {self.boost_name} | Boost value: {self.boost_value} | Needed coin: {self.needed_coin}"

# This model links users to the boosts they've used


# TaskList model that links to the User
class TaskList(models.Model):
    Taskname = models.CharField(max_length=100)
    Taskvalue = models.PositiveIntegerField(default=0)
    link = models.URLField(max_length=200, blank=True, null=True)
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

        # Create Boost and TaskList instances and associate the user
        boost = Boost.objects.create(
            boost_name="Default Boost",
            boost_value=0,
            needed_coin=0,
            level="Default"
        )
        boost.assigned_users.add(user)

        task = TaskList.objects.create(
            Taskname="Default Task",
            Taskvalue=0
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

