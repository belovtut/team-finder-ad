import json

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import LoginForm, ProfileEditForm, RegistrationForm
from .models import User
from projects.models import Skill


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("users:login")
    else:
        form = RegistrationForm()

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST, request=request)
        if form.is_valid():
            login(request, form.cleaned_data["user"])
            return redirect("projects:list")
    else:
        form = LoginForm(request=request)

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def user_detail(request, user_id):
    profile_user = get_object_or_404(
        User.objects.prefetch_related("owned_projects__participants", "skills"),
        pk=user_id,
    )
    return render(request, "users/user-details.html", {"user": profile_user})


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:detail", user_id=request.user.id)
    else:
        form = ProfileEditForm(instance=request.user)

    return render(
        request,
        "users/edit_profile.html",
        {
            "form": form,
            "user": request.user,
        },
    )


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("users:detail", user_id=request.user.id)
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "users/change_password.html", {"form": form})


def participants_list(request):
    participants = User.objects.order_by("-id")
    active_filter = None

    filter_value = request.GET.get("filter")
    if request.user.is_authenticated and filter_value:
        active_filter = filter_value
        if filter_value == "owners-of-favorite-projects":
            participants = User.objects.filter(
                owned_projects__in=request.user.favorites.all()
            ).distinct()
        elif filter_value == "owners-of-participating-projects":
            participants = User.objects.filter(
                owned_projects__in=request.user.participated_projects.all()
            ).distinct()
        elif filter_value == "interested-in-my-projects":
            participants = User.objects.filter(
                favorites__owner=request.user
            ).distinct()
        elif filter_value == "participants-of-my-projects":
            participants = (
                User.objects.filter(participated_projects__owner=request.user)
                .exclude(pk=request.user.pk)
                .distinct()
            )

    participants = participants.order_by("-id")
    paginator = Paginator(participants, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "users/participants.html",
        {
            "participants": page_obj.object_list,
            "page_obj": page_obj,
            "active_filter": active_filter,
        },
    )


def skills_search(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse([], safe=False)

    skills = Skill.objects.filter(name__icontains=query).order_by("name")[:10]
    return JsonResponse([{"id": skill.id, "name": skill.name} for skill in skills], safe=False)


@require_POST
@login_required
def skills_add(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    if request.user != target_user and not request.user.is_staff:
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

    target_user.skills.add(skill)
    return JsonResponse({"id": skill.id, "name": skill.name})


@require_POST
@login_required
def skills_remove(request, user_id, skill_id):
    target_user = get_object_or_404(User, pk=user_id)
    if request.user != target_user and not request.user.is_staff:
        return JsonResponse({"status": "error"}, status=403)

    skill = get_object_or_404(Skill, pk=skill_id)
    target_user.skills.remove(skill)
    return JsonResponse({"status": "ok"})
