from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AddMemberForm, ProjectForm
from .models import Membership, Project
from tasks.models import Task

User = get_user_model()


@login_required
def dashboard(request):
    projects = Project.objects.filter(members=request.user).distinct().order_by('-updated_at')
    tasks = Task.objects.filter(project__members=request.user).select_related('project', 'assignee')

    today = date.today()
    overdue_tasks = tasks.filter(due_date__lt=today, status__in=['todo', 'in_progress']).order_by('due_date')[:5]
    due_this_week = tasks.filter(
        due_date__gte=today,
        due_date__lte=today + timedelta(days=7),
        status__in=['todo', 'in_progress'],
    ).order_by('due_date')[:5]

    status_breakdown = list(tasks.values('status').annotate(count=Count('id')).order_by('status'))
    chart_labels = [task['status'].replace('_', ' ').title() for task in status_breakdown]
    chart_values = [task['count'] for task in status_breakdown]

    completion_by_project = []
    for project in projects:
        total = project.tasks.count()
        done = project.tasks.filter(status='done').count()
        completion = round((done / total) * 100) if total else 0
        completion_by_project.append({'project': project, 'completion': completion, 'done': done, 'total': total})

    team_workload = []
    for project in projects:
        workload = project.members.annotate(task_count=Count('assigned_tasks', filter=Q(assigned_tasks__project=project))).order_by('-task_count')
        team_workload.append({'project': project, 'members': workload})

    context = {
        'projects': projects,
        'tasks': tasks,
        'overdue_tasks': overdue_tasks,
        'due_this_week': due_this_week,
        'status_breakdown': status_breakdown,
        'chart_labels': chart_labels,
        'chart_values': chart_values,
        'completion_by_project': completion_by_project,
        'team_workload': team_workload,
    }
    return render(request, 'dashboard.html', context)


@login_required
def project_list(request):
    projects = Project.objects.filter(members=request.user).distinct().order_by('-updated_at')
    return render(request, 'projects/project_list.html', {'projects': projects})


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not project.is_member(request.user):
        messages.error(request, 'You do not have access to that project.')
        return redirect('project_list')

    tasks = project.tasks.select_related('assignee', 'created_by').order_by('-updated_at')
    members = project.members.all()
    can_manage_project = project.is_manager_or_owner(request.user)
    return render(request, 'projects/project_detail.html', {'project': project, 'tasks': tasks, 'members': members, 'can_manage_project': can_manage_project})


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, f'Project {project.name} created successfully.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'projects/project_form.html', {'form': form, 'title': 'Create Project'})


@login_required
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not project.is_manager_or_owner(request.user):
        messages.error(request, 'Only project managers can edit this project.')
        return redirect('project_detail', pk=project.pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {'form': form, 'project': project, 'title': 'Edit Project'})


@login_required
def project_archive(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not project.is_manager_or_owner(request.user):
        messages.error(request, 'Only project managers can archive this project.')
        return redirect('project_detail', pk=project.pk)

    project.is_archived = not project.is_archived
    project.save()
    status = 'archived' if project.is_archived else 'reactivated'
    messages.success(request, f'Project {project.name} has been {status}.')
    return redirect('project_detail', pk=project.pk)


@login_required
def project_members(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not project.is_manager_or_owner(request.user):
        messages.error(request, 'You do not have permission to manage members.')
        return redirect('project_detail', pk=project.pk)

    form = AddMemberForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username'].strip()
        member = User.objects.filter(Q(username=username) | Q(email=username)).first()
        if not member:
            messages.error(request, 'No user was found with that username or email.')
        elif member == request.user:
            messages.info(request, 'The owner is already part of the project.')
        elif project.members.filter(pk=member.pk).exists():
            messages.warning(request, 'That user is already in the project.')
        else:
            Membership.objects.create(project=project, user=member, role=form.cleaned_data['role'])
            messages.success(request, f'{member.username} was added to the project.')
            return redirect('project_members', pk=project.pk)

    members = project.memberships.select_related('user').order_by('user__username')
    return render(request, 'projects/project_members.html', {'project': project, 'members': members, 'form': form})
