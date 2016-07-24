import os

from django.core import mail
from django.core.urlresolvers import reverse
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings

from ..forms import ContactForm


@override_settings(ROOT_URLCONF='contact_form.tests.test_urls')
class ContactFormViewTests(TestCase):

    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'

    def tearDown(self):
        del os.environ['RECAPTCHA_TESTING']

    def test_get(self):
        """
        HTTP GET on the form view just shows the form.

        """
        contact_url = reverse('contact_form')

        response = self.client.get(contact_url)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response,
                                'contact_form/contact_form.html')

    def test_send(self):
        """
        Valid data through the view results in a successful send.

        """
        contact_url = reverse('contact_form')
        data = {'name': 'Test',
                'email': 'test@example.com',
                'title': 'Test',
                'body': 'Test message',
                'g-recaptcha-response': 'PASSED',
                }

        response = self.client.post(contact_url,
                                    data=data)

        self.assertRedirects(response,
                             reverse('contact_form_sent'))

        self.assertEqual(1, len(mail.outbox))

        message = mail.outbox[0]
        self.assertTrue(data['body'] in message.body)

        from_email = '"%s" <%s>' % (data['name'], data['email'])
        self.assertEqual(from_email, message.from_email)

        form = ContactForm(request=RequestFactory().request)
        self.assertEqual(form.recipient_list,
                         message.recipients())

    def test_invalid(self):
        """
        Invalid data doesn't work.

        """
        contact_url = reverse('contact_form')
        data = {'name': 'Test',
                'body': 'Test message'}

        response = self.client.post(contact_url,
                                    data=data)

        self.assertEqual(200, response.status_code)
        self.assertFormError(response,
                             'form',
                             'email',
                             'This field is required.')
        self.assertEqual(0, len(mail.outbox))

    def test_recipient_list(self):
        """
        Passing recipient_list when instantiating ContactFormView
        properly overrides the list of recipients.

        """
        contact_url = reverse('test_recipient_list')
        data = {'name': 'Test',
                'email': 'test@example.com',
                'title': 'Test',
                'body': 'Test message',
                'g-recaptcha-response': 'PASSED',
                }

        response = self.client.post(contact_url,
                                    data=data)
        self.assertRedirects(response,
                             reverse('contact_form_sent'))
        self.assertEqual(1, len(mail.outbox))

        message = mail.outbox[0]
        self.assertEqual(['recipient_list@example.com'],
                         message.recipients())
