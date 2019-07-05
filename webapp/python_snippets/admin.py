from django.contrib import admin

from . import models


class PythonSnippetAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'post_id', 'length', 'line_count', 'last_process_sent_p2', 'execution_time_p2',
                    'status_code_p2', 'python2_result', 'last_process_sent_p3', 'execution_time_p3', 'status_code_p3',
                    'python3_result', ]


admin.site.register(models.PythonSnippet, PythonSnippetAdmin)
