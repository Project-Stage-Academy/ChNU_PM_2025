from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from datetime import datetime

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        # Ensure that email is provided and normalize it
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        
        # Create the user without requiring a username field
        user = self.model(email=email, **extra_fields)
        
        # Set password and registration date
        user.set_password(password)
        user.registration_date = datetime.now()  # You can customize this field as needed
        user.is_active = False  # Default is inactive until verified
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Ensure superuser has staff and admin rights
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class MyUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profile_img_url = models.CharField(max_length=1000, blank=True, default="")
    phone = models.CharField(max_length=13, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False) 
    last_login = models.DateTimeField(null=True, blank=True)
    registration_date = models.DateTimeField(null=True, blank=True)  # Field to track registration date

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_set",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions_set",  
        blank=True
    )
   
    # Custom manager for user creation
    objects = CustomUserManager()

    # Use email instead of username for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name',] 
    
    def __str__(self):
        return self.email
