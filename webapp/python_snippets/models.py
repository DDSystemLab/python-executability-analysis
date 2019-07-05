from django.db import models
from django.utils import timezone
from postgres_copy import CopyManager


# Create your models here.
class PythonSnippet(models.Model):
    original_id = models.IntegerField(blank=False, null=False, unique=True)
    post_id = models.IntegerField(blank=False, null=False)
    pred_post_block_version_id = models.IntegerField(blank=True, null=True)
    root_post_block_version_id = models.IntegerField(blank=False, null=False)
    length = models.IntegerField(blank=False, null=False)
    line_count = models.IntegerField(blank=False, null=False)
    tags = models.CharField(max_length=2048, blank=False, null=False)
    content = models.TextField(blank=False, null=False)
    last_process_sent_p2 = models.DateTimeField(default=None, blank=True, null=True)
    last_process_sent_p3 = models.DateTimeField(default=None, blank=True, null=True)
    python2_result = models.TextField(blank=True, null=True)
    python3_result = models.TextField(blank=True, null=True)
    execution_time_p2 = models.FloatField(blank=True, null=True)
    execution_time_p3 = models.FloatField(blank=True, null=True)
    status_code_p2 = models.IntegerField(blank=True, null=True)
    status_code_p3 = models.IntegerField(blank=True, null=True)
    last_update = models.DateTimeField(auto_now=True)

    objects = CopyManager()

    def update_last_process_p2(self):
        self.refresh_from_db()
        self.last_process_sent_p2 = timezone.now()
        self.save()

    def update_last_process_p3(self):
        self.refresh_from_db()
        self.last_process_sent_p3 = timezone.now()
        self.save()

    def __unicode__(self):
        return '{} - {}'.format(self.id, self.original_id)

    def __str__(self):
        return self.__unicode__()

    def to_dict(self):
        return {
            'pk': self.id,
            'original_id': self.original_id,
            'post_id': self.post_id,
            'pred_post_block_version_id': self.pred_post_block_version_id,
            'root_post_block_version_id': self.root_post_block_version_id,
            'length': self.length,
            'line_count': self.line_count,
            'tags': self.tags,
            'content': self.content,
            'last_process_sent_p2': self.last_process_sent_p2,
            'last_process_sent_p3': self.last_process_sent_p3,
            'python2_result': self.python2_result,
            'python3_result': self.python3_result,
            'execution_time_p2': self.execution_time_p2,
            'execution_time_p3': self.execution_time_p3,
            'status_code_p2': self.status_code_p2,
            'status_code_p3': self.status_code_p3,
        }
