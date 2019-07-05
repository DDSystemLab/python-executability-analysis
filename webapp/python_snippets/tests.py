from django.test import TestCase

from .models import PythonSnippet

# Create your tests here.
import unittest
from django.test import Client

class SimpleTest(unittest.TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_details(self):
        ps = PythonSnippet()
        ps.original_id = 1
        ps.post_id = 1
        ps.pred_post_block_version_id = 1
        ps.root_post_block_version_id = 1
        ps.length = 1
        ps.line_count = 1
        ps.tags = '<a><b>'
        ps.content = 'Content'
        ps.save()

        # Issue a GET request.
        response1 = self.client.get('/get_new_task/2/')
        print(response1.json())
        self.assertEqual(response1.json()['python_version'], 2)
        # Check that the response is 200 OK.
        self.assertEqual(response1.status_code, 200)

        # Issue a GET request.
        response2 = self.client.get('/get_new_task/3/')
        print(response2.json())
        self.assertEqual(response2.json()['python_version'], 3)
        # Check that the response is 200 OK.
        self.assertEqual(response2.status_code, 200)

        # This time, it shouldn't work
        response1 = self.client.get('/get_new_task/2/')
        self.assertNotEqual(response1.status_code, 200)

        # This time, it shouldn't work
        response2 = self.client.get('/get_new_task/3/')
        self.assertNotEqual(response2.status_code, 200)

        res = self.client.get('/get_task/{}/'.format(ps.id))
        obj = res.json()
        self.assertNotEqual(obj['last_process_sent_p2'], None)
        self.assertNotEqual(obj['last_process_sent_p3'], None)
        self.assertEqual(obj['python2_result'], None)
        self.assertEqual(obj['status_code_p2'], None)
        self.assertEqual(obj['python3_result'], None)
        self.assertEqual(obj['status_code_p3'], None)

        payload = {
            'pk': ps.id,
            'status_code': 0,
            'result': 'A',
            'execution_time': 1
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        res = self.client.post('/update_task/2', headers=headers, data=payload, allow_redirects=False, timeout=10)
        obj = res.json()
        self.assertEqual(obj['msg'], 'OK!')


        res = self.client.get('/get_task/{}/'.format(ps.id))
        obj = res.json()
        self.assertNotEqual(obj['last_process_sent_p2'], None)
        self.assertNotEqual(obj['last_process_sent_p3'], None)
        self.assertEqual(obj['python2_result'], 'A')
        self.assertEqual(obj['status_code_p2'], 0)
        self.assertEqual(obj['execution_time_p2'], 1)
        self.assertEqual(obj['python3_result'], None)
        self.assertEqual(obj['status_code_p3'], None)
        self.assertEqual(obj['execution_time_p3'], None)
        
        # Test for python 3
        payload = {
            'pk': ps.id,
            'status_code': 1,
            'result': 'B',
            'execution_time': 2
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        res = self.client.post('/update_task/3', headers=headers, data=payload, allow_redirects=False, timeout=10)
        obj = res.json()
        self.assertEqual(obj['msg'], 'OK!')

        res = self.client.get('/get_task/{}/'.format(ps.id))
        obj = res.json()
        self.assertNotEqual(obj['last_process_sent_p2'], None)
        self.assertNotEqual(obj['last_process_sent_p3'], None)
        self.assertEqual(obj['python2_result'], 'A')
        self.assertEqual(obj['status_code_p2'], 0)
        self.assertEqual(obj['execution_time_p2'], 1)
        self.assertEqual(obj['python3_result'], 'B')
        self.assertEqual(obj['status_code_p3'], 1)
        self.assertEqual(obj['execution_time_p3'], 2)





        



