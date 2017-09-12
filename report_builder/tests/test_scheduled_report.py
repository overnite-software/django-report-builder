from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from ..tasks import report_builder_run_scheduled_report
from ..models import Report, ScheduledReport

User = get_user_model()


class ScheduledReportTests(TestCase):
    def test_scheduled_report(self):
        ct = ContentType.objects.get(model="bar", app_label="demo_models")
        report = Report.objects.create(root_model=ct, name="A")
        scheduled_report = ScheduledReport.objects.create(
            report=report,
            other_emails="test@example.com",
        )
        report_builder_run_scheduled_report(scheduled_report.id)
        scheduled_report.refresh_from_db()
        scheduled_report.report.refresh_from_db()
        self.assertIsNotNone(scheduled_report.last_run)
        self.assertIsNotNone(scheduled_report.report.report_file_creation)
        self.assertEqual(len(mail.outbox), 1)

    def test_run_scheduled_report_view(self):
        ct = ContentType.objects.get(model="bar", app_label="demo_models")
        report = Report.objects.create(root_model=ct, name="A")
        scheduled_report = ScheduledReport.objects.create(
            report=report,
            other_emails="test@example.com",
        )

        url = reverse('run_scheduled_report', kwargs={'pk': scheduled_report.id})
        user = User.objects.create(username='testy', is_staff=True, is_superuser=True)
        self.client.force_login(user)
        res = self.client.get(url)
        self.assertEqual(res.status_code, 302)