from django.test import TestCase
from django.core.mail import send_mail
# Create your tests here.


def send_test():
    send_mail(
        subject='test',
        message='test',
        from_email='dfedotov-skillfactory@yandex.ru',
        recipient_list=['dmfedotov8@gmail.com']
    )
