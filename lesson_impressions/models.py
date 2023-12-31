from django.db import models
from django.contrib.auth import get_user_model
from lesson.models import Lesson

User = get_user_model()


class Like(models.Model):
    owner = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='likes', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.owner.email} -> {self.lesson.title}'


class Dislike(models.Model):
    owner = models.ForeignKey(User, related_name='dislikes', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='dislikes', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.owner.email} -> {self.lesson.title}'


class Comment(models.Model):
    owner = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='comments', on_delete=models.CASCADE)
    body = models.TextField()
    attachment = models.FileField(upload_to=f'comment_attachments/files/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.owner}|{self.lesson}|{self.body}'
