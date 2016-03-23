from account.models import Account
from django.contrib.auth import logout
from django.contrib.auth.backends import ModelBackend
from django.shortcuts import redirect


class AccountBackend(ModelBackend):
    """
    Backend for updating how users sign in. It supports both email and password based login.
    """

    def authenticate(self, username=None, password=None, **kwargs):
        """
        Authenticates the user.
        :param username: the username or email of the account to be authenticated
        :param password: the passoword of the account
        :param kwargs: any additional arguments
        :return: a tuple of (statusString, Account)
        """
        if '@' in username:
            # email login
            try:
                account = Account.objects.get(email=username)
                if account.check_password(password):
                    return account
            except Account.DoesNotExist:
                return None
        else:
            # username login
            try:
                account = Account.objects.get(username=username)
                if account.check_password(password):
                    return account
            except Account.DoesNotExist:
                return None


def social_user(backend, uid, user=None, *args, **kwargs):
    provider = backend.name
    social = backend.strategy.storage.user.get_social_auth(provider, uid)
    if social:
        if user and social.user != user:
            logout(backend.strategy.request)
            user = None
        elif not user:
            user = social.user
    else:
        logout(backend.strategy.request)
        user = None

    return {'social': social,
            'user': user,
            'is_new': user is None,
            'new_association': False}


def redirect_if_no_refresh_token(backend, response, social, *args, **kwargs):
    import pdb
    pdb.set_trace()
    if backend.name == 'google-oauth2' and social and response.get('refresh_token') is None and social.extra_data.get(
            'refresh_token') is None:
        return redirect('/login/google-oauth2?approval_prompt=force')
