import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import Project, Skill


PROJECTS_PER_PAGE = 12


def project_list(request):
    projects = Project.objects.select_related("owner").prefetch_related("participants", "skills")
    projects = projects.order_by("-created_at")

    skills = Skill.objects.order_by("name")
    active_skill = None
    skill_param = request.GET.get("skill")
    if skill_param:
        try:
            active_skill = int(skill_param)
            projects = projects.filter(skills__id=active_skill)
        except ValueError:
            active_skill = None

    paginator = Paginator(projects, PROJECTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    favorite_ids = set()
    if request.user.is_authenticated:
        favorite_ids = set(request.user.favorites.values_list("id", flat=True))

    return render(
        request,
        "projects/project_list.html",
        {
            "projects": page_obj.object_list,
            "page_obj": page_obj,
            "skills": skills,
            "active_skill": active_skill,
            "favorite_ids": favorite_ids,
        },
    )


def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants", "skills"),
        pk=project_id,
    )

    favorite_ids = set()
    if request.user.is_authenticated:
        favorite_ids = set(request.user.favorites.values_list("id", flat=True))

    return render(
        request,
        "projects/project-details.html",
        {
            "project": project,
            "favorite_ids": favorite_ids,
        },
    )


@login_required
def favorite_projects(request):
    projects = request.user.favorites.select_related("owner").prefetch_related("participants")
    projects = projects.order_by("-created_at")

    paginator = Paginator(projects, PROJECTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    favorite_ids = set(request.user.favorites.values_list("id", flat=True))

    return render(
        request,
        "projects/favorite_projects.html",
        {"projects": page_obj.object_list, "page_obj": page_obj, "favorite_ids": favorite_ids},
    )


@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect("projects:detail", project_id=project.id)
    else:
        form = ProjectForm()

    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": False},
    )


@login_required
def project_edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Недостаточно прав")

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:detail", project_id=project.id)
    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True},
    )
@require_POST
def toggle_favorite(request, project_id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "detail": "auth_required"}, status=401)

    project = get_object_or_404(Project, pk=project_id)
    favorites = request.user.favorites

    if favorites.filter(pk=project.id).exists():
        favorites.remove(project)
        favorited = False
    else:
        favorites.add(project)
        favorited = True

    return JsonResponse({"status": "ok", "favorited": favorited})


@require_POST
@login_required
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    participants = project.participants

    if participants.filter(pk=request.user.id).exists():
        participants.remove(request.user)
        is_participant = False
    else:
        participants.add(request.user)
        is_participant = True

    return JsonResponse({"status": "ok", "participant": is_participant})


@require_POST
@login_required
def complete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user and not request.user.is_staff:
        return JsonResponse({"status": "error"}, status=403)
    if project.status != Project.STATUS_OPEN:
        return JsonResponse({"status": "error"}, status=400)

    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])

    return JsonResponse({"status": "ok", "project_status": project.status})


def skills_search(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse([], safe=False)

    skills = Skill.objects.filter(name__icontains=query).order_by("name")[:10]
    return JsonResponse([{"id": skill.id, "name": skill.name} for skill in skills], safe=False)


@require_POST
@login_required
def skills_add(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user and not request.user.is_staff:
        return JsonResponse({"status": "error"}, status=403)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        payload = {}

    skill = None
    skill_id = payload.get("skill_id")
    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    else:
        name = (payload.get("name") or "").strip()
        if not name:
            return JsonResponse({"status": "error"}, status=400)
        skill = Skill.objects.filter(name__iexact=name).first()
        if not skill:
            skill = Skill.objects.create(name=name)

    project.skills.add(skill)
    return JsonResponse({"id": skill.id, "name": skill.name})


@require_POST
@login_required
def skills_remove(request, project_id, skill_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user and not request.user.is_staff:
        return JsonResponse({"status": "error"}, status=403)

    skill = get_object_or_404(Skill, pk=skill_id)
    project.skills.remove(skill)
    return JsonResponse({"status": "ok"})
