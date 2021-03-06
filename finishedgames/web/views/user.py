from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import (Http404, HttpResponse, HttpRequest)
from django.shortcuts import (get_object_or_404, render)
from typing import Dict  # NOQA: F401

from core.forms import UserGameForm
from core.models import (Game, Platform, UserGame, WishlistedUserGame)


def _progress_bar_class(progress: int) -> str:
    # Leaving "bad" colors for low thresholds, as in general users will have high % of catalog unfinished
    if progress <= 5:
        return "is-error"
    elif 5 < progress < 25:
        return "is-warning"
    elif 25 < progress < 50:
        return "is-primary"
    else:
        return "is-success"


def users(request: HttpRequest) -> HttpResponse:
    # For security reasons, no superadmins/staff can have normal site profiles
    users = get_user_model().objects.filter(is_active=True, is_superuser=False, is_staff=False)
    context = {
        "users": users,
    }

    return render(request, "user/users.html", context)


def public_profile(request: HttpRequest, username: str) -> HttpResponse:
    viewed_user = get_object_or_404(get_user_model(), username=username)

    currently_playing_games = UserGame.objects \
                                      .filter(user=viewed_user, currently_playing=True) \
                                      .prefetch_related("game", "platform") \
                                      .order_by("-id")[:settings.LATEST_VIDEOGAMES_DISPLAY_COUNT]
    latest_finished_games = UserGame.objects \
                                    .filter(user=viewed_user) \
                                    .exclude(year_finished__isnull=True) \
                                    .prefetch_related("game", "platform") \
                                    .order_by("-year_finished", "-id")[:settings.LATEST_VIDEOGAMES_DISPLAY_COUNT]
    latest_wishlisted_games = WishlistedUserGame.objects \
                                                .filter(user=viewed_user) \
                                                .prefetch_related("game", "platform") \
                                                .order_by("game__name", "-id")[:settings.LATEST_VIDEOGAMES_DISPLAY_COUNT]  # NOQA E501

    context = {
        "viewed_user": viewed_user,
        "currently_playing_items": currently_playing_games,
        "latest_finished_items": latest_finished_games,
        "latest_wishlisted_items": latest_wishlisted_games,
    }

    return render(request, "user/public_profile.html", context)


def catalog(request: HttpRequest, username: str) -> HttpResponse:
    viewed_user = get_object_or_404(get_user_model(), username=username)

    all_user_games = UserGame.objects.filter(user=viewed_user)

    user_games = all_user_games.order_by("-id").select_related("game", "platform")
    user_games_count = len(user_games)
    # trying to use ORM's distinct() causes an extra query and always leaves usergame.id
    user_platform_ids = [user_game.platform_id for user_game in user_games]
    user_platform_ids = sorted(set(user_platform_ids))  # remove duplicates
    user_platforms = Platform.objects.filter(id__in=user_platform_ids).order_by("-id")
    user_platforms_count = len(user_platforms)

    currently_playing_games_count = all_user_games.filter(currently_playing=True).count()
    finished_games_count = all_user_games.exclude(year_finished__isnull=True).count()
    if user_games_count > 0:
        finished_games_progress = int(finished_games_count * 100 / user_games_count)
    else:
        finished_games_progress = 0
    wishlisted_games_count = WishlistedUserGame.objects.filter(user=viewed_user).count()

    context = {
        "viewed_user": viewed_user,
        "latest_user_games": user_games[:settings.LATEST_VIDEOGAMES_DISPLAY_COUNT],
        "user_games_count": user_games_count,
        "latest_user_platforms": user_platforms[:settings.LATEST_PLATFORMS_DISPLAY_COUNT],
        "user_platforms_count": user_platforms_count,
        "currently_playing_games_count": currently_playing_games_count,
        "finished_games_count": finished_games_count,
        "finished_games_progress": finished_games_progress,
        "progress_class": _progress_bar_class(finished_games_progress),
        "wishlisted_games_count": wishlisted_games_count
    }

    return render(request, "user/catalog.html", context)


def games(request: HttpRequest, username: str) -> HttpResponse:
    viewed_user = get_object_or_404(get_user_model(), username=username)

    user_games = UserGame.objects \
                         .filter(user=viewed_user) \
                         .order_by("game__name") \
                         .select_related("game", "platform")

    context = {
        "viewed_user": viewed_user,
        "user_games": user_games,
        "user_games_count": len(user_games)
    }

    return render(request, "user/games.html", context)


def platforms(request: HttpRequest, username: str) -> HttpResponse:
    viewed_user = get_object_or_404(get_user_model(), username=username)

    user_games = UserGame.objects.filter(user=viewed_user)
    # trying to use ORM's distinct() causes an extra query and always leaves usergame.id
    user_platform_ids = [user_game.platform_id for user_game in user_games]
    user_platform_ids = sorted(set(user_platform_ids))  # remove duplicates
    user_platforms = Platform.objects.filter(id__in=user_platform_ids)

    context = {
        "viewed_user": viewed_user,
        "user_platforms": user_platforms,
        "user_platforms_count": len(user_platforms)
    }

    return render(request, "user/platforms.html", context)


def currently_playing_games(request: HttpRequest, username: str) -> HttpResponse:
    viewed_user = get_object_or_404(get_user_model(), username=username)

    currently_playing_games = UserGame.objects \
                                      .filter(user=viewed_user, currently_playing=True) \
                                      .order_by("game__name") \
                                      .select_related("game", "platform")

    context = {
        "viewed_user": viewed_user,
        "currently_playing_games": currently_playing_games,
        "currently_playing_games_count": len(currently_playing_games)
    }

    return render(request, "user/currently_playing_games.html", context)


def finished_games(request: HttpRequest, username: str) -> HttpResponse:
    viewed_user = get_object_or_404(get_user_model(), username=username)

    finished_games = UserGame.objects.filter(user=viewed_user) \
                                     .exclude(year_finished__isnull=True) \
                                     .order_by("-year_finished", "game__name") \
                                     .select_related("game", "platform")

    context = {
        "viewed_user": viewed_user,
        "finished_games": finished_games,
        "finished_games_count": len(finished_games)
    }

    return render(request, "user/finished_games.html", context)


def wishlisted_games(request: HttpRequest, username: str) -> HttpResponse:
    viewed_user = get_object_or_404(get_user_model(), username=username)

    wishlisted_games = WishlistedUserGame.objects \
                                         .filter(user=viewed_user) \
                                         .order_by("game__name") \
                                         .select_related("game", "platform")

    context = {
        "viewed_user": viewed_user,
        "wishlisted_games": wishlisted_games,
        "wishlisted_games_count": len(wishlisted_games)
    }

    return render(request, "user/wishlisted_games.html", context)


def user_games_by_platform(request: HttpRequest, username: str, platform_id: int) -> HttpResponse:
    viewed_user = get_object_or_404(get_user_model(), username=username)

    platform = get_object_or_404(Platform, pk=platform_id)
    user_games = UserGame.objects \
                         .filter(user=viewed_user, platform=platform) \
                         .order_by("game__name") \
                         .select_related("game")
    games_count = len(user_games)

    currently_playing_games_count = user_games.filter(currently_playing=True).count()
    finished_games_count = user_games.exclude(year_finished__isnull=True).count()
    if games_count > 0:
        finished_games_progress = int(finished_games_count * 100 / games_count)
    else:
        finished_games_progress = 0

    context = {
        "viewed_user": viewed_user,
        "platform": platform,
        "user_games": user_games,
        "games_count": games_count,
        "currently_playing_games_count": currently_playing_games_count,
        "finished_games_count": finished_games_count,
        "finished_games_progress": finished_games_progress,
        "progress_class": _progress_bar_class(finished_games_progress),
    }

    return render(request, "user/games_by_platform.html", context)


@login_required
def profile(request: HttpRequest, username: str) -> HttpResponse:
    if username != request.user.get_username():
        raise Http404("Invalid URL")

    context = {}  # type: Dict

    return render(request, "user/profile.html", context)


@login_required
def add_game(request: HttpRequest, username: str) -> HttpResponse:
    if username != request.user.get_username():
        raise Http404("Invalid URL")

    success_message = ""
    error_message = ""

    if request.method == "POST":
        form = UserGameForm(request.POST, request.FILES)
        if form.is_valid() and int(request.POST["user"]) == request.user.id:
            user_game = form.save()
            success_message = "Game '{}' for '{}' added".format(user_game.game.name, user_game.platform.shortname)
        else:
            if form.non_field_errors:
                error_message = form.non_field_errors
            elif int(request.POST["user"]) != request.user.id:
                error_message = "Can only add games to the current logged in user"
            else:
                error_message = "There was an error and couldn't add the game"

    games = Game.objects.only("id", "name").order_by("name")
    platforms = Platform.objects.only("id", "name").order_by("name")

    context = {
        "games": games,
        "platforms": platforms,
        "error_message": error_message,
        "success_message": success_message
    }

    return render(request, "user/add_game.html", context)
