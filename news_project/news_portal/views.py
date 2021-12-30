from django.shortcuts import render
from django.views import View
# Create your views here.

from django.views.generic import TemplateView, ListView, DetailView, CreateView, DeleteView, UpdateView
from .models import Post, Category, CategoryUser, PostCategory
from django.views import View
from django.core.paginator import Paginator
from .filters import PostFilter
from .forms import PostForm, PostUpdate
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required


SOURCE_EMAIL = 'dfedotov-skillfactory@yandex.ru'

# the following is required for user notification
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

# the following is required for news letter
import datetime
from datetime import datetime
from datetime import timedelta
from django.http import HttpResponse
from django.core.cache import cache


"""
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Post)
def new_post(sender, instance, created, **kwargs):
    print('Новый пост')
    print(instance.title)
"""

# Create your views here.

'''
class PostList(ListView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-id')
'''

'''
class PostList(View):
    def get(self, request):
        posts = Post.objects.order_by('-id')
        p = Paginator(posts, 1)
        posts = p.get_page(request.GET.get('page',1))
        data = {'posts':posts}
        return render(request,'post.html',data)
'''


class PostList(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'news_portal/post.html'
    context_object_name = 'posts'
    ordering = ['-id']
    paginate_by = 8

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        context['is_author'] = self.request.user.groups.filter(name='authors').exists()
        context['categories'] = Category.objects.all()
        context['form'] = PostForm()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
        return super().get(request, *args, **kwargs)


class PostDetail(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'news_portal/post_detail.html'
    context_object_name = 'post_detail'
    queryset = Post.objects.all()

    def get_object(self, *args, **kwargs):                      # cache usage
        obj = cache.get(f'post-{self.kwargs["pk"]}', None)      # get from cache
        if not obj:                                             # if not in cache
            obj = super().get_object()                          # get object
            cache.set(f'post-{self.kwargs["pk"]}', obj)
            print('from db')
        return obj


notification = {}


def check_user(request):                                        # check request user
    author_id = int(request.POST['author'])
    category_id = int(request.POST['category'])                 # category id as integer
    this_category = Category.objects.get(id=category_id)        # this category
    categories = CategoryUser.objects.filter(category=this_category)    # user subscriptions for this category
    receivers=[]
    for c in categories:                                        # is user subscribed
        receivers.append(c.user.id)                             # add to the list of receivers
    if len(receivers):                                          # do we have any receivers?
        notification[author_id]=receivers                       # add the list to notification


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news_portal.add_post',)
    template_name = 'news_portal/create_post.html'
    form_class = PostForm
    success_url = '/'

    def post(self, request, *args, **kwargs):
        check_user(request)
        return super().post(self, request, *args, **kwargs)


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('news_portal.delete_post',)
    template_name = 'news_portal/delete_post.html'
    context_object_name = 'post_detail'
    queryset = Post.objects.all()
    success_url = '/'


class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news_portal.change_post',)
    template_name = 'news_portal/update_post.html'
    form_class = PostUpdate
    success_url = '/'

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk = id)


@login_required
def upgrade_me(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
    return redirect('/')


class CategoryList(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'news_portal/category.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['is_author'] = user.groups.filter(name='authors').exists()
        subscriptions = []
        cu = CategoryUser.objects.all()
        subscriptions = []
        for x in cu:
            if x.user == user:
                c = x.category
                subscriptions.append(c.name)
        context['subscriptions'] = subscriptions
        return context


@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)
    category.save()
    return redirect('/category')


@login_required
def unsubscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.remove(user)
    category.save()
    return redirect('/category')

# the list of new posts with user subscriptions


def new_user_posts(user):
    cu = CategoryUser.objects.all()
    subscriptions = []  # user subscriptions
    for x in cu:
        if x.user == user:  # this user?
            c = x.category  # add category
            subscriptions.append(x.category)  # to the list of categories

    old_date = datetime.now() - timedelta(days=7)  # new posts
    new_posts = Post.objects.filter(time_stamp__range=[old_date, datetime.now()])

    pc = PostCategory.objects.all()  # category filter
    posts = []
    for post in new_posts:
        for y in pc:
            if y.post == post:  # is it this post?
                if y.category in subscriptions:  # is category in subscriptions?
                    posts.append(post)  # add post to the list
    return posts


class NewPosts(ListView):
    model = Post
    template_name = 'news_portal/new_posts.html'
    context_object_name = 'new_posts'
    ordering = ['-id']
    paginate_by = 8

    def get_queryset(self):                             # list of new posts
        user = self.request.user                        # current user
        return new_user_posts(user)


mail_sent = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <h1> Список новых постов отправлен на вашу почту </h1>
</body>
</html>
"""

no_news = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <h1> Новых постов нет </h1>
</body>
</html>
"""


class UserInformer():

    def __init__(self):
        self.category_user = CategoryUser.objects.all()     # ctegory -> user
        self.post_category = PostCategory.objects.all()     # post -> category
        old_date = datetime.now() - timedelta(days=7)       # new posts
        self.new_posts = Post.objects.filter(time_stamp__range=[old_date, datetime.now()])

    def new_user_posts(self, user):
        subscriptions = []                          # user subscriptions
        for x in self.category_user:
            if x.user == user:  # this user?
                c = x.category  # add category
                subscriptions.append(x.category)    # to the list of subscriptions

        old_date = datetime.now() - timedelta(days=7)  # new posts
        new_posts = Post.objects.filter(time_stamp__range=[old_date, datetime.now()])

        posts = []                                          # empty list
        if subscriptions:                                   # has user any subscriptions?
            for post in new_posts:
                for y in self.post_category:
                    if y.post == post:                      # is it this post?
                        if y.category in subscriptions:     # is category in subscriptions?
                            posts.append(post)              # add post to the list
        return posts

    def send_news_to_user(self, user, new_posts):
        new_posts = new_user_posts(user)
        if new_posts:
                html_content = render_to_string('news_portal/new_list.html', {'new_posts': new_posts})

        msg = EmailMultiAlternatives(                       # the message itself
            subject='news_portal',
            body='test',
            from_email=SOURCE_EMAIL,
            to=[user.email]
            )
        msg.attach_alternative(html_content, "text/html")   # html content
        msg.send()                                          # send message


@login_required
def send_news(request):                                     # send_news view
    user = request.user
    informer = UserInformer()
    new_posts = informer.new_user_posts(user)
    if new_posts:
        informer.send_news_to_user(user, new_posts)         # send message
        return HttpResponse(mail_sent)
    else:
        return HttpResponse(no_news)


# celery test
from django.http import HttpResponse
from django.views import View
from .tasks import hello


class TestView(View):

    def get(self, request):
        hello.delay()
        return HttpResponse('Hello!')











