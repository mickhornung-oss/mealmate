from typing import Any

from app.models import User

NavItem = dict[str, Any]

NAV_ITEMS: list[NavItem] = [
    {
        "key": "nav.discover",
        "label_fallback": "Rezepte entdecken",
        "href": "/",
        "method": "GET",
        "roles": ["guest", "user", "admin"],
        "class_name": "nav-link",
    },
    {
        "key": "nav.submit",
        "label_fallback": "Rezept einreichen",
        "href": "/submit",
        "method": "GET",
        "roles": ["guest", "user"],
        "class_name": "nav-link",
    },
    {
        "key": "nav.login",
        "label_fallback": "Anmelden",
        "href": "/login",
        "method": "GET",
        "roles": ["guest"],
        "class_name": "btn btn-secondary",
    },
    {
        "key": "nav.register",
        "label_fallback": "Registrieren",
        "href": "/register",
        "method": "GET",
        "roles": ["guest"],
        "class_name": "btn btn-primary",
    },
    {
        "key": "nav.publish_recipe",
        "label_fallback": "Rezept veröffentlichen",
        "href": "/recipes/new",
        "method": "GET",
        "roles": ["admin"],
        "class_name": "nav-link",
    },
    {
        "key": "nav.admin",
        "label_fallback": "Admin",
        "href": "/admin",
        "method": "GET",
        "roles": ["admin"],
        "class_name": "nav-link",
    },
    {
        "key": "nav.admin_submissions",
        "label_fallback": "Moderation",
        "href": "/admin/submissions",
        "method": "GET",
        "roles": ["admin"],
        "class_name": "nav-link",
    },
    {
        "key": "nav.my_submissions",
        "label_fallback": "Meine Einreichungen",
        "href": "/my-submissions",
        "method": "GET",
        "roles": ["user"],
        "class_name": "nav-link",
    },
    {
        "key": "nav.favorites",
        "label_fallback": "Favoriten",
        "href": "/favorites",
        "method": "GET",
        "roles": ["user"],
        "class_name": "nav-link",
    },
    {
        "key": "nav.profile",
        "label_fallback": "Mein Profil",
        "href": "/me",
        "method": "GET",
        "roles": ["user", "admin"],
        "class_name": "nav-link",
    },
    {
        "key": "nav.logout",
        "label_fallback": "Abmelden",
        "href": "/logout",
        "method": "POST",
        "roles": ["user", "admin"],
        "class_name": "btn btn-primary",
    },
]


def _role_name(user: User | None) -> str:
    if user is None:
        return "guest"
    if user.role == "admin":
        return "admin"
    return "user"


def build_nav_items(user: User | None) -> list[NavItem]:
    role = _role_name(user)
    return [dict(item) for item in NAV_ITEMS if role in item["roles"]]
