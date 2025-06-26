from django.contrib.auth.models import PermissionsMixin, BaseUserManager
from django.db import models


from django.contrib.auth.models import AbstractUser


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, fio, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(fio=fio, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, fio, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(fio, email, password, **extra_fields)

    def create_superuser(self, fio, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(fio, email, password, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    username = None
    email = models.EmailField(unique=True)
    fio = models.CharField(max_length=120)
    USERNAME_FIELD = "email"
    objects = UserManager()
    REQUIRED_FIELDS = [
        "fio",
    ]
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Пользователя"
        verbose_name_plural = "Пользователи"
        ordering = ["email"]

    def has_perm_in_workspace(self, perm_code: str, workspace) -> bool:
        roles = self.workspace_roles.filter(workspace=workspace).select_related("role")
        for user_role in roles:
            if user_role.role.role_permissions.filter(permission__code=perm_code).exists():
                return True
        return False


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Permission(models.Model):
    code = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.code


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role_permissions")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name="permission_roles")

    class Meta:
        unique_together = ("role", "permission")

    def __str__(self):
        return f"{self.role.name} — {self.permission.code}"
