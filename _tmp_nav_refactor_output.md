Geaenderte Dateien kurz:
1. `app/nav.py`
2. `app/views.py`
3. `app/templates/base.html`
4. `docs/NAV_AUDIT.md`
5. `tests/test_nav_roles.py`

### app/nav.py
```python
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
        "label_fallback": "Rezept veroeffentlichen",
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

```
ZEILEN-ERKLAERUNG
1. Diese Zeile importiert benoetigte Python-Module oder Symbole.
2. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
3. Diese Zeile importiert benoetigte Python-Module oder Symbole.
4. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
5. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
6. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
7. Diese Zeile oeffnet eine mehrzeilige Daten- oder Aufrufstruktur.
8. Diese Zeile oeffnet eine mehrzeilige Daten- oder Aufrufstruktur.
9. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
10. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
11. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
12. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
13. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
14. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
15. Diese Zeile schliesst eine zuvor geoeffnete Struktur korrekt ab.
16. Diese Zeile oeffnet eine mehrzeilige Daten- oder Aufrufstruktur.
17. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
18. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
19. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
20. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
21. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
22. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
23. Diese Zeile schliesst eine zuvor geoeffnete Struktur korrekt ab.
24. Diese Zeile oeffnet eine mehrzeilige Daten- oder Aufrufstruktur.
25. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
26. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
27. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
28. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
29. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
30. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
31. Diese Zeile schliesst eine zuvor geoeffnete Struktur korrekt ab.
32. Diese Zeile oeffnet eine mehrzeilige Daten- oder Aufrufstruktur.
33. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
34. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
35. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
36. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
37. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
38. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
39. Diese Zeile schliesst eine zuvor geoeffnete Struktur korrekt ab.
40. Diese Zeile oeffnet eine mehrzeilige Daten- oder Aufrufstruktur.
41. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
42. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
43. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
44. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
45. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
46. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
47. Diese Zeile schliesst eine zuvor geoeffnete Struktur korrekt ab.
48. Diese Zeile oeffnet eine mehrzeilige Daten- oder Aufrufstruktur.
49. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
50. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
51. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
52. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
53. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
54. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
55. Diese Zeile schliesst eine zuvor geoeffnete Struktur korrekt ab.
56. Diese Zeile oeffnet eine mehrzeilige Daten- oder Aufrufstruktur.
57. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
58. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
59. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
60. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
61. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
62. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
63. Diese Zeile schliesst eine zuvor geoeffnete Struktur korrekt ab.
64. Diese Zeile oeffnet eine mehrzeilige Daten- oder Aufrufstruktur.
65. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
66. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
67. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
68. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
69. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
70. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
71. Diese Zeile schliesst eine zuvor geoeffnete Struktur korrekt ab.
72. Diese Zeile oeffnet eine mehrzeilige Daten- oder Aufrufstruktur.
73. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
74. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
75. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
76. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
77. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
78. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
79. Diese Zeile schliesst eine zuvor geoeffnete Struktur korrekt ab.
80. Diese Zeile oeffnet eine mehrzeilige Daten- oder Aufrufstruktur.
81. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
82. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
83. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
84. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
85. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
86. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
87. Diese Zeile schliesst eine zuvor geoeffnete Struktur korrekt ab.
88. Diese Zeile oeffnet eine mehrzeilige Daten- oder Aufrufstruktur.
89. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
90. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
91. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
92. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
93. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
94. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
95. Diese Zeile schliesst eine zuvor geoeffnete Struktur korrekt ab.
96. Diese Zeile schliesst eine zuvor geoeffnete Struktur korrekt ab.
97. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
98. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
99. Diese Zeile definiert eine Funktion fuer gekapselte Programm-Logik.
100. Diese Zeile steuert einen bedingten Verzweigungsablauf im Code.
101. Diese Zeile gibt einen berechneten Wert aus der Funktion zurueck.
102. Diese Zeile steuert einen bedingten Verzweigungsablauf im Code.
103. Diese Zeile gibt einen berechneten Wert aus der Funktion zurueck.
104. Diese Zeile gibt einen berechneten Wert aus der Funktion zurueck.
105. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
106. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
107. Diese Zeile definiert eine Funktion fuer gekapselte Programm-Logik.
108. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
109. Diese Zeile gibt einen berechneten Wert aus der Funktion zurueck.

### app/views.py
```python
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context

from app.i18n import datetime_de, difficulty_label, role_label, submission_status_label, t
from app.i18n.service import available_langs
from app.nav import build_nav_items


class MealMateTemplates(Jinja2Templates):
    def TemplateResponse(self, *args, **kwargs):
        if args and isinstance(args[0], str):
            name = args[0]
            context = args[1] if len(args) > 1 else kwargs.get("context")
            if isinstance(context, dict) and context.get("request") is not None:
                request = context["request"]
                return super().TemplateResponse(
                    request,
                    name,
                    context,
                    status_code=kwargs.get("status_code", 200),
                    headers=kwargs.get("headers"),
                    media_type=kwargs.get("media_type"),
                    background=kwargs.get("background"),
                )
        return super().TemplateResponse(*args, **kwargs)


templates = MealMateTemplates(directory="app/templates")


@pass_context
def jinja_t(context, key: str, **kwargs):
    request = context.get("request")
    return t(key, request=request, **kwargs)


@pass_context
def jinja_difficulty_label(context, value: str | None):
    request = context.get("request")
    return difficulty_label(value, request=request)


@pass_context
def jinja_role_label(context, value: str | None):
    request = context.get("request")
    return role_label(value, request=request)


@pass_context
def jinja_submission_status_label(context, value: str | None):
    request = context.get("request")
    return submission_status_label(value, request=request)


@pass_context
def jinja_datetime_label(context, value):
    request = context.get("request")
    return datetime_de(value, request=request)


def lang_url(request, code: str) -> str:
    return str(request.url.include_query_params(lang=code))


templates.env.globals["t"] = jinja_t
templates.env.globals["difficulty_label"] = jinja_difficulty_label
templates.env.globals["role_label"] = jinja_role_label
templates.env.globals["submission_status_label"] = jinja_submission_status_label
templates.env.globals["available_langs"] = available_langs()
templates.env.globals["lang_url"] = lang_url
templates.env.globals["get_nav_items"] = build_nav_items
templates.env.filters["datetime_de"] = jinja_datetime_label


def redirect(url: str, status_code: int = 303) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=status_code)

```
ZEILEN-ERKLAERUNG
1. Diese Zeile importiert benoetigte Python-Module oder Symbole.
2. Diese Zeile importiert benoetigte Python-Module oder Symbole.
3. Diese Zeile importiert benoetigte Python-Module oder Symbole.
4. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
5. Diese Zeile importiert benoetigte Python-Module oder Symbole.
6. Diese Zeile importiert benoetigte Python-Module oder Symbole.
7. Diese Zeile importiert benoetigte Python-Module oder Symbole.
8. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
9. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
10. Diese Zeile definiert eine Python-Klasse fuer strukturierte Logik.
11. Diese Zeile definiert eine Funktion fuer gekapselte Programm-Logik.
12. Diese Zeile steuert einen bedingten Verzweigungsablauf im Code.
13. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
14. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
15. Diese Zeile steuert einen bedingten Verzweigungsablauf im Code.
16. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
17. Diese Zeile gibt einen berechneten Wert aus der Funktion zurueck.
18. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
19. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
20. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
21. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
22. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
23. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
24. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
25. Diese Zeile schliesst eine zuvor geoeffnete Struktur korrekt ab.
26. Diese Zeile gibt einen berechneten Wert aus der Funktion zurueck.
27. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
28. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
29. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
30. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
31. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
32. Diese Zeile setzt einen Decorator auf die folgende Funktion.
33. Diese Zeile definiert eine Funktion fuer gekapselte Programm-Logik.
34. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
35. Diese Zeile gibt einen berechneten Wert aus der Funktion zurueck.
36. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
37. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
38. Diese Zeile setzt einen Decorator auf die folgende Funktion.
39. Diese Zeile definiert eine Funktion fuer gekapselte Programm-Logik.
40. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
41. Diese Zeile gibt einen berechneten Wert aus der Funktion zurueck.
42. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
43. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
44. Diese Zeile setzt einen Decorator auf die folgende Funktion.
45. Diese Zeile definiert eine Funktion fuer gekapselte Programm-Logik.
46. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
47. Diese Zeile gibt einen berechneten Wert aus der Funktion zurueck.
48. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
49. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
50. Diese Zeile setzt einen Decorator auf die folgende Funktion.
51. Diese Zeile definiert eine Funktion fuer gekapselte Programm-Logik.
52. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
53. Diese Zeile gibt einen berechneten Wert aus der Funktion zurueck.
54. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
55. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
56. Diese Zeile setzt einen Decorator auf die folgende Funktion.
57. Diese Zeile definiert eine Funktion fuer gekapselte Programm-Logik.
58. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
59. Diese Zeile gibt einen berechneten Wert aus der Funktion zurueck.
60. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
61. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
62. Diese Zeile definiert eine Funktion fuer gekapselte Programm-Logik.
63. Diese Zeile gibt einen berechneten Wert aus der Funktion zurueck.
64. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
65. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
66. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
67. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
68. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
69. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
70. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
71. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
72. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
73. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
74. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
75. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
76. Diese Zeile definiert eine Funktion fuer gekapselte Programm-Logik.
77. Diese Zeile gibt einen berechneten Wert aus der Funktion zurueck.

### app/templates/base.html
```html
<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="csrf-token" content="{{ csrf_token or '' }}">
  <title>{{ title or t("app.name") }}</title>
  <link rel="stylesheet" href="/static/style.css">
  <script src="/static/htmx.min.js"></script>
  <script src="/static/security.js" defer></script>
</head>
<body>
  <a href="#main" class="skip-link">Zum Inhalt springen</a>
  <header class="topbar">
    <div class="topbar-inner">
      <a href="/" class="brand">{{ t("app.name") }}</a>
      <nav class="main-nav">
        {% for item in get_nav_items(current_user) %}
        {% set translated = t(item.key) %}
        {% set label = translated if translated != item.key else item.label_fallback %}
        {% set is_active = request.url.path == item.href or (item.href != "/" and request.url.path.startswith(item.href + "/")) %}
        {% if item.method == "POST" %}
        <form method="post" action="{{ item.href }}" class="inline">
          <input type="hidden" name="csrf_token" value="{{ csrf_token or '' }}">
          <button type="submit" class="{{ item.class_name }}{% if is_active %} active{% endif %}">{{ label }}</button>
        </form>
        {% else %}
        <a class="{{ item.class_name }}{% if is_active %} active{% endif %}" href="{{ item.href }}">{{ label }}</a>
        {% endif %}
        {% endfor %}
        <div class="lang-switch">
          <span class="lang-label">{{ t("nav.language") }}</span>
          <div class="lang-links">
            {% for code, label in available_langs %}
            <a href="{{ lang_url(request, code) }}" class="lang-link {% if current_lang == code %}active{% endif %}" {% if current_lang == code %}aria-current="page"{% endif %}>{{ label }}</a>
            {% endfor %}
          </div>
        </div>
      </nav>
    </div>
  </header>
  <main id="main" class="container">
    {% if message %}
    <p class="flash flash-success">{{ message }}</p>
    {% endif %}
    {% if error %}
    <p class="flash flash-error">{{ error }}</p>
    {% endif %}
    {% block content %}{% endblock %}
  </main>
</body>
</html>

```
ZEILEN-ERKLAERUNG
1. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
2. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
3. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
4. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
5. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
6. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
7. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
8. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
9. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
10. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
11. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
12. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
13. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
14. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
15. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
16. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
17. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
18. Diese Zeile steuert die Jinja-Template-Logik fuer die Navigation oder Anzeige.
19. Diese Zeile steuert die Jinja-Template-Logik fuer die Navigation oder Anzeige.
20. Diese Zeile steuert die Jinja-Template-Logik fuer die Navigation oder Anzeige.
21. Diese Zeile steuert die Jinja-Template-Logik fuer die Navigation oder Anzeige.
22. Diese Zeile steuert die Jinja-Template-Logik fuer die Navigation oder Anzeige.
23. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
24. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
25. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
26. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
27. Diese Zeile steuert die Jinja-Template-Logik fuer die Navigation oder Anzeige.
28. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
29. Diese Zeile steuert die Jinja-Template-Logik fuer die Navigation oder Anzeige.
30. Diese Zeile steuert die Jinja-Template-Logik fuer die Navigation oder Anzeige.
31. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
32. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
33. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
34. Diese Zeile steuert die Jinja-Template-Logik fuer die Navigation oder Anzeige.
35. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
36. Diese Zeile steuert die Jinja-Template-Logik fuer die Navigation oder Anzeige.
37. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
38. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
39. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
40. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
41. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
42. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
43. Diese Zeile steuert die Jinja-Template-Logik fuer die Navigation oder Anzeige.
44. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
45. Diese Zeile steuert die Jinja-Template-Logik fuer die Navigation oder Anzeige.
46. Diese Zeile steuert die Jinja-Template-Logik fuer die Navigation oder Anzeige.
47. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
48. Diese Zeile steuert die Jinja-Template-Logik fuer die Navigation oder Anzeige.
49. Diese Zeile steuert die Jinja-Template-Logik fuer die Navigation oder Anzeige.
50. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
51. Diese Zeile definiert ein HTML-Element der Seitenstruktur.
52. Diese Zeile definiert ein HTML-Element der Seitenstruktur.

### docs/NAV_AUDIT.md
```markdown
# NAV Audit

Stand: 2026-03-03

## Renderer-Ansatz

- Die Navbar wird zentral ueber `app/nav.py` mit `build_nav_items(user)` erzeugt.
- `base.html` rendert nur noch eine einzige Schleife ueber `get_nav_items(current_user)`.
- GET-Links werden als `<a>` und POST-Links (Logout) als `<form method="post">` mit CSRF gerendert.

## Rollenmatrix

| Rolle | Linktext-Key | Route | Methode |
|---|---|---|---|
| guest | `nav.discover` | `/` | GET |
| guest | `nav.submit` | `/submit` | GET |
| guest | `nav.login` | `/login` | GET |
| guest | `nav.register` | `/register` | GET |
| user | `nav.discover` | `/` | GET |
| user | `nav.submit` | `/submit` | GET |
| user | `nav.my_submissions` | `/my-submissions` | GET |
| user | `nav.favorites` | `/favorites` | GET |
| user | `nav.profile` | `/me` | GET |
| user | `nav.logout` | `/logout` | POST |
| admin | `nav.discover` | `/` | GET |
| admin | `nav.publish_recipe` | `/recipes/new` | GET |
| admin | `nav.admin` | `/admin` | GET |
| admin | `nav.admin_submissions` | `/admin/submissions` | GET |
| admin | `nav.profile` | `/me` | GET |
| admin | `nav.logout` | `/logout` | POST |

## Redundanz-Befund

1. Der Admin-Link `Rezept einreichen` (`/submit`) wurde aus der Admin-Navigation entfernt.
2. Admin nutzt jetzt eindeutig `Rezept veroeffentlichen` (`/recipes/new`) fuer direkte Veroeffentlichung.
3. Die alte Rollen-`if/elif`-Linkverdrahtung in `base.html` wurde durch eine zentrale Nav-Datenstruktur ersetzt.


```
ZEILEN-ERKLAERUNG
1. Diese Zeile ist eine Markdown-Ueberschrift zur Struktur des Dokuments.
2. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
3. Diese Zeile beschreibt den Audit-Kontext in kurzer Textform.
4. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
5. Diese Zeile ist eine Markdown-Ueberschrift zur Struktur des Dokuments.
6. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
7. Diese Zeile listet einen Audit-Punkt als Stichpunkt auf.
8. Diese Zeile listet einen Audit-Punkt als Stichpunkt auf.
9. Diese Zeile listet einen Audit-Punkt als Stichpunkt auf.
10. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
11. Diese Zeile ist eine Markdown-Ueberschrift zur Struktur des Dokuments.
12. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
13. Diese Zeile ist Teil der Audit-Tabelle in Markdown-Form.
14. Diese Zeile ist Teil der Audit-Tabelle in Markdown-Form.
15. Diese Zeile ist Teil der Audit-Tabelle in Markdown-Form.
16. Diese Zeile ist Teil der Audit-Tabelle in Markdown-Form.
17. Diese Zeile ist Teil der Audit-Tabelle in Markdown-Form.
18. Diese Zeile ist Teil der Audit-Tabelle in Markdown-Form.
19. Diese Zeile ist Teil der Audit-Tabelle in Markdown-Form.
20. Diese Zeile ist Teil der Audit-Tabelle in Markdown-Form.
21. Diese Zeile ist Teil der Audit-Tabelle in Markdown-Form.
22. Diese Zeile ist Teil der Audit-Tabelle in Markdown-Form.
23. Diese Zeile ist Teil der Audit-Tabelle in Markdown-Form.
24. Diese Zeile ist Teil der Audit-Tabelle in Markdown-Form.
25. Diese Zeile ist Teil der Audit-Tabelle in Markdown-Form.
26. Diese Zeile ist Teil der Audit-Tabelle in Markdown-Form.
27. Diese Zeile ist Teil der Audit-Tabelle in Markdown-Form.
28. Diese Zeile ist Teil der Audit-Tabelle in Markdown-Form.
29. Diese Zeile ist Teil der Audit-Tabelle in Markdown-Form.
30. Diese Zeile ist Teil der Audit-Tabelle in Markdown-Form.
31. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
32. Diese Zeile ist eine Markdown-Ueberschrift zur Struktur des Dokuments.
33. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
34. Diese Zeile beschreibt einen konkreten Redundanz-Befund als nummerierten Punkt.
35. Diese Zeile beschreibt einen konkreten Redundanz-Befund als nummerierten Punkt.
36. Diese Zeile beschreibt einen konkreten Redundanz-Befund als nummerierten Punkt.
37. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.

### tests/test_nav_roles.py
```python
from app.models import User
from app.security import hash_password, normalize_username


def _create_user(db, *, email: str, password: str, role: str = "user", username: str | None = None) -> User:
    user = User(
        email=email.strip().lower(),
        username=username,
        username_normalized=normalize_username(username) if username else None,
        hashed_password=hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _csrf_token(client, path: str = "/login") -> str:
    response = client.get(path)
    assert response.status_code == 200
    token = client.cookies.get("csrf_token")
    assert token
    return str(token)


def _login(client, *, identifier: str, password: str) -> None:
    csrf = _csrf_token(client, "/login")
    response = client.post(
        "/login",
        data={
            "identifier": identifier,
            "password": password,
            "csrf_token": csrf,
        },
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert response.status_code in {302, 303}


def _extract_nav_block(html: str) -> str:
    start = html.find('<nav class="main-nav">')
    assert start >= 0
    end = html.find("</nav>", start)
    assert end > start
    return html[start:end]


def test_guest_nav_has_submit_but_not_publish(client):
    response = client.get("/")
    assert response.status_code == 200
    nav_html = _extract_nav_block(response.text)
    assert 'href="/submit"' in nav_html
    assert 'href="/recipes/new"' not in nav_html
    assert 'href="/login"' in nav_html
    assert 'href="/register"' in nav_html


def test_user_nav_has_submit_and_my_submissions_but_not_publish(client, db_session_factory):
    with db_session_factory() as db:
        _create_user(
            db,
            email="nav-user@example.local",
            password="NavUserPass123!",
            role="user",
            username="nav.user",
        )

    _login(client, identifier="nav-user@example.local", password="NavUserPass123!")
    response = client.get("/")
    assert response.status_code == 200
    nav_html = _extract_nav_block(response.text)
    assert 'href="/submit"' in nav_html
    assert 'href="/my-submissions"' in nav_html
    assert 'href="/favorites"' in nav_html
    assert 'href="/me"' in nav_html
    assert 'href="/recipes/new"' not in nav_html


def test_admin_nav_has_publish_and_admin_but_not_submit(client, db_session_factory):
    with db_session_factory() as db:
        _create_user(
            db,
            email="nav-admin@example.local",
            password="NavAdminPass123!",
            role="admin",
            username="nav.admin",
        )

    _login(client, identifier="nav-admin@example.local", password="NavAdminPass123!")
    response = client.get("/")
    assert response.status_code == 200
    nav_html = _extract_nav_block(response.text)
    assert 'href="/recipes/new"' in nav_html
    assert 'href="/admin"' in nav_html
    assert 'href="/admin/submissions"' in nav_html
    assert 'href="/submit"' not in nav_html

```
ZEILEN-ERKLAERUNG
1. Diese Zeile importiert benoetigte Python-Module oder Symbole.
2. Diese Zeile importiert benoetigte Python-Module oder Symbole.
3. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
4. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
5. Diese Zeile definiert eine Funktion fuer gekapselte Programm-Logik.
6. Diese Zeile oeffnet eine mehrzeilige Daten- oder Aufrufstruktur.
7. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
8. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
9. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
10. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
11. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
12. Diese Zeile schliesst eine zuvor geoeffnete Struktur korrekt ab.
13. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
14. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
15. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
16. Diese Zeile gibt einen berechneten Wert aus der Funktion zurueck.
17. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
18. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
19. Diese Zeile definiert eine Funktion fuer gekapselte Programm-Logik.
20. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
21. Diese Zeile prueft eine Bedingung als Test- oder Sicherheits-Assertion.
22. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
23. Diese Zeile prueft eine Bedingung als Test- oder Sicherheits-Assertion.
24. Diese Zeile gibt einen berechneten Wert aus der Funktion zurueck.
25. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
26. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
27. Diese Zeile definiert eine Funktion fuer gekapselte Programm-Logik.
28. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
29. Diese Zeile oeffnet eine mehrzeilige Daten- oder Aufrufstruktur.
30. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
31. Diese Zeile oeffnet eine mehrzeilige Daten- oder Aufrufstruktur.
32. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
33. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
34. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
35. Diese Zeile schliesst eine zuvor geoeffnete Struktur korrekt ab.
36. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
37. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
38. Diese Zeile schliesst eine zuvor geoeffnete Struktur korrekt ab.
39. Diese Zeile prueft eine Bedingung als Test- oder Sicherheits-Assertion.
40. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
41. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
42. Diese Zeile definiert eine Funktion fuer gekapselte Programm-Logik.
43. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
44. Diese Zeile prueft eine Bedingung als Test- oder Sicherheits-Assertion.
45. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
46. Diese Zeile prueft eine Bedingung als Test- oder Sicherheits-Assertion.
47. Diese Zeile gibt einen berechneten Wert aus der Funktion zurueck.
48. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
49. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
50. Diese Zeile definiert eine Funktion fuer gekapselte Programm-Logik.
51. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
52. Diese Zeile prueft eine Bedingung als Test- oder Sicherheits-Assertion.
53. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
54. Diese Zeile prueft eine Bedingung als Test- oder Sicherheits-Assertion.
55. Diese Zeile prueft eine Bedingung als Test- oder Sicherheits-Assertion.
56. Diese Zeile prueft eine Bedingung als Test- oder Sicherheits-Assertion.
57. Diese Zeile prueft eine Bedingung als Test- oder Sicherheits-Assertion.
58. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
59. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
60. Diese Zeile definiert eine Funktion fuer gekapselte Programm-Logik.
61. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
62. Diese Zeile oeffnet eine mehrzeilige Daten- oder Aufrufstruktur.
63. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
64. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
65. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
66. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
67. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
68. Diese Zeile schliesst eine zuvor geoeffnete Struktur korrekt ab.
69. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
70. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
71. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
72. Diese Zeile prueft eine Bedingung als Test- oder Sicherheits-Assertion.
73. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
74. Diese Zeile prueft eine Bedingung als Test- oder Sicherheits-Assertion.
75. Diese Zeile prueft eine Bedingung als Test- oder Sicherheits-Assertion.
76. Diese Zeile prueft eine Bedingung als Test- oder Sicherheits-Assertion.
77. Diese Zeile prueft eine Bedingung als Test- oder Sicherheits-Assertion.
78. Diese Zeile prueft eine Bedingung als Test- oder Sicherheits-Assertion.
79. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
80. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
81. Diese Zeile definiert eine Funktion fuer gekapselte Programm-Logik.
82. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
83. Diese Zeile oeffnet eine mehrzeilige Daten- oder Aufrufstruktur.
84. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
85. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
86. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
87. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
88. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
89. Diese Zeile schliesst eine zuvor geoeffnete Struktur korrekt ab.
90. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
91. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
92. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
93. Diese Zeile prueft eine Bedingung als Test- oder Sicherheits-Assertion.
94. Diese Zeile traegt zur Implementierung der zentralen Navigation bei.
95. Diese Zeile prueft eine Bedingung als Test- oder Sicherheits-Assertion.
96. Diese Zeile prueft eine Bedingung als Test- oder Sicherheits-Assertion.
97. Diese Zeile prueft eine Bedingung als Test- oder Sicherheits-Assertion.
98. Diese Zeile prueft eine Bedingung als Test- oder Sicherheits-Assertion.