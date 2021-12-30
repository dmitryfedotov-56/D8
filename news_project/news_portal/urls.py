from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', PostList.as_view(), name = 'post_list'),
    path('show/<int:pk>', PostDetail.as_view(), name = 'post_detail'),
    path('create/', PostCreate.as_view(), name='create_post'),
    path('delete/<int:pk>', PostDelete.as_view(), name='delete_post'),
    path('update/<int:pk>', PostUpdate.as_view(), name='update_post'),
    path('logout/', LogoutView.as_view(template_name='news_portal/logout.html'), name='logout'),
    path('upgrade/', upgrade_me, name='upgrade'),
    path('category/', CategoryList.as_view(), name='category'),
    path('subscribe/<int:pk>', subscribe, name='subscribe'),
    path('unsubscribe/<int:pk>', unsubscribe, name='unsubscribe'),
    path('new_posts/', send_news, name='new_posts'),
    path('test/', TestView.as_view(), name='test'),
]

