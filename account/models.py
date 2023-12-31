from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **kwargs):
        if not email:
            return ValueError('Email was not handed')
        email = self.normalize_email(email=email)
        user = self.model(email=email, **kwargs)
        user.create_activation_code()
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password, **kwargs):
        kwargs.setdefault('is_staff', False)
        kwargs.setdefault('is_superuser', False)
        return self._create_user(email, password, **kwargs)

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_active', True)
        if kwargs.get('is_staff') is not True:
            raise ValueError('SuperUser must be a staff, currently not!')
        if kwargs.get('is_superuser') is not True:
            raise ValueError('SuperUser must be a superuser, currently not!')
        return self._create_user(email, password, **kwargs)


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    balance = models.DecimalField(decimal_places=2, max_digits=9, default=0)
    avatar = models.ImageField(upload_to='avatars', blank=True, null=True, default='images/defAv.png')
    activation_code = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=50, unique=True, blank=True, null=True)
    is_active = models.BooleanField(
        default=False, help_text='This field is for user activation'
    )
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def create_activation_code(self):
        import uuid

        code = str(uuid.uuid4())
        self.activation_code = code
