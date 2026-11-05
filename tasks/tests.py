from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Task


class TaskAPITestCase(APITestCase):

    def setUp(self):
        self.task1 = Task.objects.create(title="Task one", description="first")
        self.task2 = Task.objects.create(title="Task two", status=Task.Status.DONE)
        self.list_url = reverse('task-list')

    def detail_url(self, pk):
        return reverse('task-detail', args=[pk])

    def toggle_url(self, pk):
        return reverse('task-toggle', args=[pk])

    # ---------- ایجاد ----------

    def test_create_task_success(self):
        payload = {'title': 'New task', 'description': 'some text'}
        response = self.client.post(self.list_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New task')
        self.assertEqual(response.data['status'], 'not_started') 
        self.assertIn('id', response.data)
        self.assertEqual(Task.objects.count(), 3)

    def test_create_task_without_description(self):
        response = self.client.post(self.list_url, {'title': 'Only title'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['description'], '')

    def test_create_ignores_read_only_fields(self):
        payload = {'title': 'Hack', 'id': 999}
        response = self.client.post(self.list_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data['id'], 999)

    # ---------- لیست و جزئیات ----------

    def test_list_tasks(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_task(self):
        response = self.client.get(self.detail_url(self.task1.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.task1.id)
        self.assertEqual(response.data['title'], 'Task one')

    # ---------- ویرایش ----------

    def test_put_updates_all_fields(self):
        payload = {'title': 'Replaced', 'description': 'new desc', 'status': 'done'}
        response = self.client.put(self.detail_url(self.task1.id), payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, 'Replaced')
        self.assertEqual(self.task1.description, 'new desc')
        self.assertEqual(self.task1.status, 'done')


    def test_patch_updates_partial(self):
        response = self.client.patch(self.detail_url(self.task1.id), {'status': 'doing'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, 'doing')
        self.assertEqual(self.task1.title, 'Task one')

    # ---------- حذف ----------

    def test_delete_task(self):
        response = self.client.delete(self.detail_url(self.task1.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task1.id).exists())

    # ---------- toggle ----------

    def test_toggle_flips_status(self):
        response = self.client.patch(self.toggle_url(self.task1.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'done')
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, 'done')
    
    def test_toggle_twice_returns_to_original(self):
        self.client.patch(self.toggle_url(self.task1.id))
        response = self.client.patch(self.toggle_url(self.task1.id))

        self.assertEqual(response.data['status'], 'not_started')

    def test_toggle_wrong_method(self):
        response = self.client.get(self.toggle_url(self.task1.id))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # ---------- اعتبارسنجی ----------

    def test_create_empty_title(self):
        response = self.client.post(self.list_url, {'title': ''}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_create_whitespace_title(self):
        response = self.client.post(self.list_url, {'title': '   '}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_create_missing_title(self):
        response = self.client.post(self.list_url, {'description': 'no title'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_create_title_too_long(self):
        response = self.client.post(self.list_url, {'title': 'a' * 201}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_title_max_length_boundary(self):
        response = self.client.post(self.list_url, {'title': 'a' * 200}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_put_without_title(self):
        response = self.client.put(
            self.detail_url(self.task1.id), {'description': 'x'}, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_empty_title(self):
        response = self.client.patch(
            self.detail_url(self.task1.id), {'title': ''}, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.title, 'Task one')

    # ---------- شناسه ناموجود ----------

    def test_nonexistent_id_returns_404(self):
        missing = 99999

        self.assertEqual(
            self.client.get(self.detail_url(missing)).status_code, status.HTTP_404_NOT_FOUND
        )
        self.assertEqual(
            self.client.put(self.detail_url(missing), {'title': 'x'}, format='json').status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            self.client.patch(self.detail_url(missing), {'title': 'x'}, format='json').status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            self.client.delete(self.detail_url(missing)).status_code, status.HTTP_404_NOT_FOUND
        )
        self.assertEqual(
            self.client.patch(self.toggle_url(missing)).status_code, status.HTTP_404_NOT_FOUND
        )

        # ---------- وضعیت‌ها ----------

    def test_default_status_is_not_started(self):
        response = self.client.post(self.list_url, {'title': 'x'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'not_started')

    def test_all_valid_statuses_accepted(self):
        for value in ['not_started', 'doing', 'done', 'fail']:
            response = self.client.patch(
                self.detail_url(self.task1.id), {'status': value}, format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['status'], value)

    def test_invalid_status_rejected(self):
        response = self.client.patch(
            self.detail_url(self.task1.id), {'status': 'finished'}, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, 'not_started')

    def test_toggle_from_done_goes_to_not_started(self):
        response = self.client.patch(self.toggle_url(self.task2.id))

        self.assertEqual(response.data['status'], 'not_started')

    def test_toggle_from_doing_or_fail_goes_to_done(self):
        for value in ['doing', 'fail']:
            Task.objects.filter(id=self.task1.id).update(status=value)
            response = self.client.patch(self.toggle_url(self.task1.id))
            self.assertEqual(response.data['status'], 'done')