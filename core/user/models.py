from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models import TextChoices

class MyUserRoleEnum(TextChoices):
    STANDARD_USER = 'standard_user', 'Обычный пользователь'
    MANAGER = 'admin', 'Админ'

class MyUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, role=MyUserRoleEnum.STANDARD_USER, **extra_fields):
        user = self.model(username=username, email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(username=username, email=email, password=password, role=MyUserRoleEnum.MANAGER)
        user.is_admin = True
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    username = models.CharField(max_length=30, verbose_name='Имя пользователя')
    email = models.EmailField(unique=True, verbose_name='Почта')
    phone_number = models.CharField(max_length=15, null=True, blank=True, verbose_name='Номер телефона')
    avatar = models.ImageField(upload_to='media/user_avatar/', null=True, blank=True, verbose_name='Аватарка')
    address = models.CharField(max_length=150, null=True, blank=True, verbose_name='Адрес')
    first_name = models.CharField(max_length=30, null=True, blank=True, verbose_name='Имя')
    last_name = models.CharField(max_length=30, null=True, blank=True, verbose_name='Фамилия')
    is_2fa_enabled = models.BooleanField(default=False, verbose_name="Двухфакторка")
    is_admin = models.BooleanField(default=False, verbose_name='Админ')
    role = models.CharField(
        max_length=20,
        choices=MyUserRoleEnum.choices,
        default=MyUserRoleEnum.STANDARD_USER,
        verbose_name='Роль пользователя'
    )

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    def __str__(self):
        return f'{self.email}'

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1, verbose_name='Пользователя')
    code = models.CharField(max_length=6, verbose_name='Код')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Одноразовый код"
        verbose_name_plural = "Одноразовые коды"

    def __str__(self):
        return f"{self.user.username} - {self.code}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'