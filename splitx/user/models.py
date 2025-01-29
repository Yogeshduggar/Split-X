from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid as uu
from enum import Enum

class Collage(models.Model):
    id = models.UUIDField(primary_key=True, default=uu.uuid1, editable=False)
    name = models.CharField(max_length=100)
    domain = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "collages"

class Batch(models.Model):
    id = models.UUIDField(primary_key=True, default=uu.uuid1, editable=False)
    collage = models.ForeignKey(Collage, on_delete=models.CASCADE)
    course = models.CharField(max_length=100)
    year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "batches"


class CustomUserManager(BaseUserManager):
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)
    
        
class Transaction(models.Model):
    class TransactionCategory(models.TextChoices):
        DEBIT = 'Debit'
        CREDIT = 'Credit'

    class ExpenseType(models.TextChoices):
        INCOME = 'Income'
        FOOD = 'Expense'
        TRANSFER = 'Transfer'
        ENTERTAINMENT = 'Entertainment'
        SHOPPING = 'Shopping'
        TRAVEL = 'Travel'
        ACADEMICS = 'Academics'

    id = models.UUIDField(primary_key=True, default=uu.uuid1, editable=False)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=100, choices=TransactionCategory.choices)
    category = models.CharField(max_length=100, choices=ExpenseType.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uu.uuid1, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    user_admin = models.ManyToManyField('User', related_name='group_admin')
    users = models.ManyToManyField('User')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Settlement(models.Model):
    class SettlementStatus(models.TextChoices):
        PENDING = 'Pending'
        SETTLED = 'Settled'
    id = models.UUIDField(primary_key=True, default=uu.uuid1, editable=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='settlements', null=True, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=100, choices=SettlementStatus.choices, default=SettlementStatus.PENDING)
    user_to_pay = models.ForeignKey('User', related_name='user_to_pay', on_delete=models.CASCADE)
    user_to_be_paid = models.ForeignKey('User', related_name='user_to_be_paid', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uu.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, related_name='batch_users')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email
