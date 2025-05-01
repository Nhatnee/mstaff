"""
WSGI config for m_staff project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'm_staff.settings')

application = get_wsgi_application()

# Chạy tạo superuser nếu chưa tồn tại
try:
    from .create_superuser import run
    run()
except Exception as e:
    pass  # Hoặc in ra lỗi nếu bạn đang debug

