from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

from .models import PythonSnippet
import random


@csrf_exempt
def get_task(request, pk):
    snippet = get_object_or_404(PythonSnippet, pk=pk)
    return JsonResponse(snippet.to_dict())


@csrf_exempt
def clear_everything(request):
    all_snippets = PythonSnippet.objects.all()

    for snippet in all_snippets:
        snippet.last_process_sent_p2 = None
        snippet.last_process_sent_p3 = None
        snippet.python2_result = None
        snippet.execution_time_p2 = None
        snippet.status_code_p2 = None
        snippet.python3_result = None
        snippet.execution_time_p3 = None
        snippet.status_code_p3 = None
        snippet.save()

    return JsonResponse({
        'msg': 'OK!',
        'code': 200,
    })


@csrf_exempt
def get_new_task(request, python_version=2):
    # Check for valid python version
    python_version = int(python_version)
    if python_version != 2 and python_version != 3:
        return HttpResponseBadRequest('Bad Python Version')

    last_process_threshold = timezone.now() - timezone.timedelta(minutes=10)

    if python_version == 2:
        snippets = PythonSnippet.objects.filter(
            Q(last_process_sent_p2__isnull=True) |
            Q(last_process_sent_p2__lte=last_process_threshold, status_code_p2__isnull=True)
        )
    else:
        snippets = PythonSnippet.objects.filter(
            Q(last_process_sent_p3__isnull=True) |
            Q(last_process_sent_p3__lte=last_process_threshold, status_code_p3__isnull=True)
        )

    # if len(snippets) == 0:
    #     return HttpResponseBadRequest('No more snippets left')

    # Choose an snippet randomly
    # snippet = snippets[random.randint(0, len(snippets) - 1)]
    # snippet = snippets[random.randint(0, 100)]
    try:
        snippet = snippets[0]
    except Exception:
        return HttpResponseBadRequest('No more snippets left')

    # update the last process
    if python_version == 2:
        snippet.update_last_process_p2()
    else:
        snippet.update_last_process_p3()

    # Save the changes
    if python_version == 2:
        snippet.save(update_fields=["last_process_sent_p2"])
        # snippet.update(last_process_sent_p2= timezone.now())
    else:
        snippet.save(update_fields=["last_process_sent_p3"])
        # snippet.update(last_process_sent_p3= timezone.now())

    obj = snippet.to_dict()
    obj['python_version'] = python_version

    return JsonResponse(obj)


@csrf_exempt
def update_task(request, python_version=2):
    # Check for valid python version
    python_version = int(python_version)
    if python_version != 2 and python_version != 3:
        return HttpResponseBadRequest('Bad Python Version')

    pk = int(request.POST.get('pk', ''))
    snippet = get_object_or_404(PythonSnippet, pk=pk)

    if python_version == 2:
        snippet.python2_result = str(request.POST.get('result', ''))
        snippet.execution_time_p2 = str(request.POST.get('execution_time', ''))
        snippet.status_code_p2 = int(request.POST.get('status_code', ''))
        fields = ["python2_result", "execution_time_p2", "status_code_p2"]
    else:
        snippet.python3_result = str(request.POST.get('result', ''))
        snippet.execution_time_p3 = str(request.POST.get('execution_time', ''))
        snippet.status_code_p3 = int(request.POST.get('status_code', ''))
        fields = ["python3_result", "execution_time_p3", "status_code_p3"]

    snippet.save(update_fields=fields)

    return JsonResponse({
        'msg': 'OK!',
        'code': 200,
    })
