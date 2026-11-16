from django.contrib.auth import get_user_model
from django.test import TestCase

from projects.models import Membership, Project

User = get_user_model()


class ProjectMembershipTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='manager', password='secret123')
        self.project = Project.objects.create(name='Launch Campaign', owner=self.user)

    def test_owner_membership_is_created(self):
        membership = Membership.objects.get(project=self.project, user=self.user)
        self.assertEqual(membership.role, 'owner')

    def test_project_creation_creates_only_one_owner_membership(self):
        memberships = Membership.objects.filter(project=self.project, user=self.user)
        self.assertEqual(memberships.count(), 1)
