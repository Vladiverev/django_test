from django.db import models
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey


# Create your models here.


class Post(models.Model):
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(
        default=timezone.now)
    published_date = models.DateTimeField(
        blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title


class Comment(MPTTModel):
    post = models.ForeignKey('blog_test.Post', on_delete=models.CASCADE, related_name='comments')
    author = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)
    parent = TreeForeignKey('self', on_delete=models.CASCADE,  null=True, blank=True, related_name='children', db_index=True)

    def approve(self):
        self.approved_comment = True
        self.save()

    class MPTTMeta:
        # comments on one level will be ordered by date of creation
        order_insertion_by = ['created_date']

    def __str__(self):
        return self.text




