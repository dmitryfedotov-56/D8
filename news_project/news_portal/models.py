from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.core.cache import cache


class Author(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    rating = models.SmallIntegerField(default=0)

    def __str__(self):
        return f'{self.user.username}'

    def update_rating(self):
        self.rating = 0
        author_comments = self.user.comment_set.all()
        for c in author_comments:                   # for all comments by this author
            self.rating += c.rating                 # increase rating
        author_posts = self.post_set.all()
        for p in author_posts:                      # for all articles by this author
            if p.post_type == ARTICLE:              # if it is an article
                self.rating += p.rating * 3         # increase rating
                p_comments = p.comment_set.all()
                for c in p_comments:                # for all comments on this article
                    self.rating += c.rating         # increase rating
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    subscribers = models.ManyToManyField(User, through='CategoryUser')  # category subscribers

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f'{self.name}'


NEWS = 'NW'
ARTICLE = 'AR'

POST_DICT = {NEWS:'Новость',ARTICLE:'Статья'}

POST_TYPES = tuple(POST_DICT.items())


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=2, choices = POST_TYPES, default = NEWS)
    time_stamp = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.SmallIntegerField(default=0)

    def __str__(self):
        return f'{POST_DICT[self.post_type]} "{self.title}"'

    def get_absolute_url(self):
        return f'/news/show/{self.id}'

    def like(self):         # post like
        self.rating += 1
        self.save()

    def dislike(self):      # post dislike
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[0:124] + '...'

    def category_list(self):
        s = ''
        n = 0
        for category in self.category.all():
            if( n != 0): s = s + ', '
            n = n + 1
            s = s + str(category)
        return s

    def post_info(self, header):
        print(header)
        print(f'Название    : {self.title}')
        print(f'Рейтинг     : {self.rating}')
        print(f'Coздано     : {self.time_stamp}')
        print(f'Автор       : {self.author.user.username}')
        print(f'Рейтинг     : {self.author.rating}')
        print(f'Темы        : {self.category_list()}')
        print(f'Превью      : {self.preview()}')

    def comment_list(self):
        c_list = self.comment_set.all()
        print(f'Комментарии к статье "{self.title}"')
        for c in c_list: print(c.text)

    def save(self, *args, **kwargs):        # save is redefined
        super().save(*args, **kwargs)       # save model
        cache.delete(f'post-{self.pk}')     # delete cache


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment_author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    time_stamp = models.DateTimeField(auto_now_add=True)
    rating = models.SmallIntegerField(default=0)

    def __str__(self):
        return f'Комментарий на "{self.post.title}"'

    def like(self):         # comment like
        self.rating += 1
        self.save()

    def dislike(self):      # comment dislike
        self.rating -= 1
        self.save()


# new relation between Category and User.

class CategoryUser(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
