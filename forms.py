from django import forms

from .models import Membership, Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class AddMemberForm(forms.Form):
    username = forms.CharField(max_length=150, label='Username or email')
    role = forms.ChoiceField(choices=Membership.ROLE_CHOICES)
