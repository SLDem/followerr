from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        user = self._create_user(email, password, True, True, **extra_fields)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    objects: models.Manager()
    objects = UserManager()

    email = models.EmailField('Email', max_length=254, unique=True)
    name = models.CharField('Full Name', max_length=35, unique=True, null=False, blank=False)
    city = models.CharField('City', max_length=100, null=True, blank=True)
    gender = models.BooleanField('Gender', null=True, blank=False)
    following = models.CharField('Following', max_length=254, null=True, blank=True)

    last_online = models.DateTimeField(blank=True, null=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    about_me = models.TextField('About me', max_length=5000, null=True, blank=True)
    favourite_music = models.TextField('Favourite music', max_length=3000, null=True, blank=True)
    favourite_books = models.TextField('Favourite books', max_length=3000, null=True, blank=True)
    favourite_movies = models.TextField('Favourite movies', max_length=3000, null=True, blank=True)

    friends = models.ManyToManyField("User", blank=True)
    blocked_users = models.ManyToManyField("User", blank=True, related_name='blocked_by_user')
    avatar = models.ForeignKey("photoalbums.Image", on_delete=models.SET_NULL, null=True, blank=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_absolute_url(self):
        return '/users/%i' % self.pk

    def __str__(self):
        return self.name


