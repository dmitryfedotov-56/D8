from django.db.models.signals import post_save
from allauth.account.signals import email_confirmed
from django.dispatch import receiver
from .models import Post
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User
from .models import POST_DICT, PostCategory
from .views import notification, SOURCE_EMAIL


@receiver(email_confirmed)
def email_confirmed_(request, email_address, **kwargs):
    print(f'User aсtivated email={email_address}')

    html_content = render_to_string(                # html to send
        'news_portal/user_activated.html',{}
    )

    msg = EmailMultiAlternatives(                   # the message itself
        subject='activation on news-portal',
        body='test',
        from_email='dfedotov-skillfactory@yandex.ru',
        to=[email_address]
    )

    msg.attach_alternative(html_content, "text/html")   # html content
    msg.send()                                          # send message


@receiver(post_save, sender=Post)
def new_post(sender, instance, created, **kwargs):

    """
    # no categories!!!
    print('Темы')
    pc = PostCategory.objects.all()
    for x in pc:
        if x.post.id == instance.id:
            print(x.category)
    print('Конец списка')
    """

    author_id = instance.author.id

    if author_id in notification:                           # author id in notifications

        html_content = render_to_string(                    # html to send
            'news_portal/post_created.html',
            {
                'post_title': instance.title,
                'post_author': instance.author,
                'post_text': instance.text,
                'post_type': POST_DICT[instance.post_type],
                'post_id': instance.id
            }
        )

        msg = EmailMultiAlternatives(  # the message itself
            subject='news_portal',
            body='test',
            from_email=SOURCE_EMAIL,
            to=[]
        )
        msg.attach_alternative(html_content, "text/html")  # html content

        for user_id in notification[author_id]:             # the list of receivers
            user_email = User.objects.get(id=user_id).email
            msg.to.append(user_email)
            print(f'Посылем mail на {user_email}')

        msg.send()                                          # send message

        del notification[author_id]                         # clear list

        """
        send_mail(
            subject = 'news_portal',
            message = instance.title,
            from_email = SOURCE_EMAIL,
            recipient_list = ['dmfedotov8@gmail.com']
        )
        """


