from django.db import models

class Task(models.Model):
    class Status(models.TextChoices):
            NOT_STARTED = 'not_started', 'Not started'
            DOING = 'doing', 'Doing'
            DONE = 'done', 'Done'
            FAIL = 'fail', 'Failed'


    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
         max_length=20,
         choices=Status.choices,
         default=Status.NOT_STARTED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title