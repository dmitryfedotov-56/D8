from django.forms import ModelForm
from .models import Post
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group


class PostForm(ModelForm):

    class Meta:
        model = Post
        fields = ['author', 'title', 'post_type', 'category', 'text']


class PostUpdate(ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'post_type', 'category', 'text']


class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)
        return user

