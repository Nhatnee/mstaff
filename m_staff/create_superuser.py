# create_superuser.py

from django.contrib.auth import get_user_model

def run():
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@.com',
            password='123'
        )
