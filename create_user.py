from django.contrib.auth.models import User

def create_superuser():
    user = User.objects.create_superuser("admin",'admin@gmail.com','helloworld')
    user.save()

create_superuser()

