from celery import shared_task
import time
from .views import UserInformer
from django.contrib.auth.models import User


@shared_task
def hello():
    time.sleep(10)
    print("Hello, world!")


@shared_task
def inform_users():
    users = User.objects.all()
    informer = UserInformer()
    for user in users:
        post_list = informer.new_user_posts(user)
        if post_list: informer.send_news_to_user(user, post_list)