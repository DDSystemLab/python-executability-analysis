import requests
import traceback

base_url = 'http://206.12.88.44:30296'


def get_new_task(python_version=2):
    python_version = int(python_version)
    if python_version != 2 and python_version != 3:
        print('Bad Python Version')
        return None

    url = base_url + '/get_new_task/{}'.format(python_version)
    headers = {}
    try:
        response = requests.request('GET', url, headers=headers, allow_redirects=False, timeout=10)
        return response.json()
    except Exception:
        traceback.print_stack()
        return None


def get_task(pk):
    url = base_url + '/get_task/{}'.format(pk)
    headers = {}
    try:
        response = requests.request('GET', url, headers=headers, allow_redirects=False, timeout=10)
        return response.json()
    except Exception:
        traceback.print_stack()
        return None


def update_task(python_version, task_pk, status_code, result, execution_time):
    python_version = int(python_version)
    if python_version != 2 and python_version != 3:
        print('Bad Python Version')
        return False

    url = base_url + '/update_task/{}'.format(python_version)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'pk': task_pk,
        'status_code': status_code,
        'result': result,
        'execution_time': execution_time
    }

    try:
        response = requests.request('POST', url, headers=headers, data=payload, allow_redirects=False, timeout=10)
        print(response.text)
        return True
    except Exception:
        traceback.print_stack()
        return False


if __name__ == '__main__':
    task = get_new_task(python_version=2)

    # If we actually got something
    if task is not None:
        print(task)

    update_task(python_version=2, task_pk=task['pk'], status_code=0, result='something very strange',
                execution_time=5.3)

    task = get_task(task['pk'])
    print(task)
