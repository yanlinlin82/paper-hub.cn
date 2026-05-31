"""
Django views for the group pages (legacy - now redirects to React SPA).
The SPA at the frontend handles all page rendering.
"""

from django.http import HttpResponse
from django.shortcuts import redirect

from config import settings
from core.models import GroupProfile

_FRONTEND_DEV_URL = "http://localhost:5173"


def _get_frontend_url(request, path=""):
    """Get the frontend SPA URL for redirects.

    In development (DEBUG=True), redirects to the Vite dev server
    to avoid redirect loops within Django itself.
    In production, returns a relative path served by Apache/Nginx.
    """
    if path.startswith("/"):
        path = path[1:]
    if settings.DEBUG:
        return f"{_FRONTEND_DEV_URL}/{path}"
    return f"/{path}"


def index_page(request, group_name):
    """Redirect to the SPA's group index page."""
    return redirect(_get_frontend_url(request, f"group/{group_name}"))


def my_sharing_page(request, group_name):
    """Redirect to the SPA's my sharing page."""
    return redirect(_get_frontend_url(request, f"group/{group_name}/my_sharing"))


def all_page(request, group_name):
    """Redirect to the SPA's all reviews page."""
    query = request.GET.get("q", "").strip()
    path = f"group/{group_name}/all"
    if query:
        path += f"?q={query}"
    return redirect(_get_frontend_url(request, path))


def recent_page(request, group_name):
    """Redirect to the SPA's recent reviews page."""
    return redirect(_get_frontend_url(request, f"group/{group_name}/recent"))


def this_month_page(request, group_name):
    """Redirect to the SPA's this month page."""
    return redirect(_get_frontend_url(request, f"group/{group_name}/this_month"))


def last_month_page(request, group_name):
    """Redirect to the SPA's last month page."""
    return redirect(_get_frontend_url(request, f"group/{group_name}/last_month"))


def trash_page(request, group_name):
    """Redirect to the SPA's trash page."""
    return redirect(_get_frontend_url(request, f"group/{group_name}/trash"))


def single_page(request, group_name, id):
    """Redirect to the SPA's single review page."""
    return redirect(_get_frontend_url(request, f"group/{group_name}/review/{id}"))


def journal_page(request, group_name, journal_name):
    """Redirect to the SPA's journal reviews page."""
    from urllib.parse import quote, unquote

    journal_name = unquote(journal_name)
    return redirect(
        _get_frontend_url(request, f"group/{group_name}/journal/{quote(journal_name)}")
    )


def user_page(request, id, group_name):
    """Redirect to the SPA's user reviews page."""
    return redirect(_get_frontend_url(request, f"group/{group_name}/user/{id}"))


def rank_page(request, group_name):
    """Redirect to the SPA's rank page."""
    return redirect(_get_frontend_url(request, f"group/{group_name}/rank"))


def rank_type_page(request, group_name, rank_type):
    """Redirect to the SPA's rank type page."""
    return redirect(_get_frontend_url(request, f"group/{group_name}/rank/{rank_type}"))
