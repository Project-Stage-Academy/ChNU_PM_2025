from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.timezone import now
from django.core.validators import RegexValidator


ukraine_phone_regex = RegexValidator(
    regex=r'^\+380\d{9}$',
    message="Phone number must be in the format: '+380XXXXXXXXX' (total 13 characters)."
)


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
        user.registration_date = now()  
        user.is_active = False  
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
       
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

class MyUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profile_img_url = models.URLField(blank=True, default="")
    phone = models.CharField(validators=[ukraine_phone_regex], max_length=13, blank=True)
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


class BlacklistedToken(models.Model):
    token = models.CharField(max_length=500, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token
