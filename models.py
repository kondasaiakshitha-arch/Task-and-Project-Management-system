from django.conf import settings
from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_projects')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Membership', related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        created = self.pk is None
        super().save(*args, **kwargs)
        if created:
            Membership.objects.get_or_create(project=self, user=self.owner, role='owner')

    def is_member(self, user):
        return self.members.filter(pk=user.pk).exists()

    def is_manager_or_owner(self, user):
        return self.memberships.filter(user=user, role__in=['owner', 'manager']).exists()


class Membership(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('manager', 'Manager'),
        ('member', 'Member'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_memberships')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')

    class Meta:
        unique_together = ('user', 'project')

    def __str__(self):
        return f'{self.user.username} ({self.role}) in {self.project.name}'
