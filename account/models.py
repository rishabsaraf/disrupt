from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _


class AccountManager(BaseUserManager):
    """
    The manager class for Account.
    """
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        :param username: the username.
        :param email: the email address
        :param password: the password
        :param extra_fields: any additional fields.
        :return: the user object
        :raises: ValueError: in case the username or email is not provided.
        """
        if not username:
            raise ValueError('The given username must be set')
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        """
        Creates a normal user.
        :param username: the username.
        :param email: the email address.
        :param password: the password, defaults to none.
        :param extra_fields: any additional fields.
        :return: the user object.
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        """
        Creates a super user.
        :param username: the username.
        :param email: the email address.
        :param password: the password.
        :param extra_fields: any additional fields
        :return: the created user.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)


class Account(AbstractBaseUser, PermissionsMixin):
    """
    Account class implementing a fully featured User model with
    admin-compliant permissions.

    Username, email and password are required. Other fields are optional.
    """
    username = models.CharField(
        _('username'),
        max_length=30,
        unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, digits and ./_ only.'),
        validators=[
            RegexValidator(
                r'^[\w.]+$',
                _('Enter a valid username. This value may contain only '
                  'letters, numbers ' 'and ./_ characters.')
            ),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=False, unique=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), auto_now=True)
    updated_on = models.DateTimeField(_('profile last updated'), auto_now_add=True)

    objects = AccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = False

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        :return: the first_name plus the last_name with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        :return: the short name of the user.
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends email to the user.
        :param subject: the subject of the email.
        :param message: the email message.
        :param from_email: the sender email address. defaults to none.
        :param kwargs: any additional parameters
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def delete(self, using=None, keep_parents=False):
        """
        This function deletes the user account. The account is not deleted actually, but only the visibility is changed.
        :param using: # TODO: check the usage of this field. defaults to none.
        :param keep_parents: boolean to decide whether to keep the parent object. defaults to false.
        """
        self.is_active = False
        self.save()
