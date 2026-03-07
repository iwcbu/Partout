from django.apps import AppConfig


class PartoutConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "partout"

    def ready(self):
        import os

        new_password = os.environ.get("RESET_ADMIN_PASSWORD")
        if not new_password:
            return

        try:
            from django.contrib.auth.models import User
            user = User.objects.filter(username="admin").first()
            if user:
                user.set_password(new_password)
                user.is_staff = True
                user.is_superuser = True
                user.save()
        except Exception:
            pass