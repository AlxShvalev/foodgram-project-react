from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )

    def __str__(self):
        user = self.user.get_full_name()
        author = self.author.get_full_name()
        return f'{user} подписан на {author}'

    class Meta:
        verbose_name = 'Подпискии'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follows',
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='follower_and_author_can_not_be_equal',
            )
        ]