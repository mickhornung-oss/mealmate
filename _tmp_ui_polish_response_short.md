Geaenderte Dateien: `app/templates/base.html`, `app/templates/home.html`, `app/templates/partials/recipe_list.html`, `app/static/style.css`.

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
        <a class="nav-link" href="/">{{ t("nav.discover") }}</a>
        <a class="nav-link" href="/submit">{{ t("nav.submit") }}</a>
        {% if current_user %}
        {% if current_user.role == "admin" %}
        <a class="nav-link" href="/recipes/new">{{ t("nav.publish_recipe") }}</a>
        {% endif %}
        <a class="nav-link" href="/my-recipes">{{ t("nav.my_recipes") }}</a>
        <a class="nav-link" href="/my-submissions">{{ t("nav.my_submissions") }}</a>
        <a class="nav-link" href="/favorites">{{ t("nav.favorites") }}</a>
        <a class="nav-link" href="/me">{{ t("nav.profile") }}</a>
        {% if current_user.role == "admin" %}
        <a class="nav-link" href="/admin">{{ t("nav.admin") }}</a>
        <a class="nav-link" href="/admin/submissions">{{ t("nav.admin_submissions") }}</a>
        {% endif %}
        <form method="post" action="/logout" class="inline">
          <button type="submit" class="btn btn-primary">{{ t("nav.logout") }}</button>
        </form>
        {% else %}
        <a class="btn btn-secondary" href="/login">{{ t("nav.login") }}</a>
        <a class="btn btn-primary" href="/register">{{ t("nav.register") }}</a>
        {% endif %}
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
1. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
2. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
3. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
4. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
5. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
6. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
7. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
8. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
9. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
10. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
11. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
12. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
13. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
14. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
15. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
16. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
17. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
18. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
19. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
20. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
21. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
22. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
23. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
24. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
25. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
26. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
27. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
28. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
29. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
30. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
31. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
32. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
33. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
34. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
35. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
36. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
37. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
38. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
39. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
40. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
41. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
42. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
43. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
44. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
45. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
46. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
47. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
48. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
49. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
50. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
51. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
52. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
53. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
54. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
55. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
56. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
57. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
58. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
59. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
60. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.

### app/templates/home.html
```html
{% extends "base.html" %}
{% block content %}
<section class="page-grid">
  <aside class="sidebar">
    <form class="sidebar-card sidebar-form" hx-get="/" hx-target="#recipe-list" hx-push-url="true">
      <h1 class="sidebar-title">{{ t("discover.title") }}</h1>
      <button type="submit" class="btn btn-primary sidebar-apply">{{ t("discover.filter.apply") }}</button>
      <label class="field">
      <span class="field-label">{{ t("discover.filter.title_contains") }}</span>
      <input type="text" name="title" value="{{ title }}" placeholder="{{ t('discover.filter.title_contains') }}">
      </label>
      <label class="field">
      <span class="field-label">{{ t("discover.filter.category") }}</span>
      <select name="category">
        <option value="">{{ t("home.all_categories") }}</option>
        {% for option in category_options %}
        <option value="{{ option }}" {% if category == option %}selected{% endif %}>{{ option }}</option>
        {% endfor %}
      </select>
      </label>
      <label class="field">
      <span class="field-label">{{ t("discover.filter.difficulty") }}</span>
      <select name="difficulty">
        <option value="">{{ t("discover.filter.difficulty") }}</option>
        <option value="easy" {% if difficulty == "easy" %}selected{% endif %}>{{ t("difficulty.easy") }}</option>
        <option value="medium" {% if difficulty == "medium" %}selected{% endif %}>{{ t("difficulty.medium") }}</option>
        <option value="hard" {% if difficulty == "hard" %}selected{% endif %}>{{ t("difficulty.hard") }}</option>
      </select>
      </label>
      <label class="field">
      <span class="field-label">{{ t("discover.filter.ingredient") }}</span>
      <input type="text" name="ingredient" value="{{ ingredient }}" placeholder="{{ t('discover.filter.ingredient') }}">
      </label>
      <label class="field">
      <span class="field-label">Sort</span>
      <select name="sort">
        <option value="date" {% if sort == "date" %}selected{% endif %}>{{ t("discover.sort.newest") }}</option>
        <option value="prep_time" {% if sort == "prep_time" %}selected{% endif %}>{{ t("discover.sort.prep_time") }}</option>
        <option value="avg_rating" {% if sort == "avg_rating" %}selected{% endif %}>{{ t("discover.sort.rating_desc") }}</option>
      </select>
      </label>
      <label class="field">
      <span class="field-label">{{ t("home.per_page") }}</span>
      <select name="per_page">
        {% for option in per_page_options %}
        <option value="{{ option }}" {% if per_page == option %}selected{% endif %}>{{ option }}</option>
        {% endfor %}
      </select>
      </label>
      <label class="field">
      <span class="field-label">{{ t("discover.filter.image") }}</span>
      <select name="image_filter">
        <option value="">{{ t("discover.filter.all_images") }}</option>
        <option value="with_image" {% if image_filter == "with_image" %}selected{% endif %}>{{ t("discover.filter.with_image") }}</option>
      </select>
      </label>
    </form>
  </aside>
  <section class="content" aria-live="polite">
    <section id="recipe-list" class="recipe-list-shell">
      {% include "partials/recipe_list.html" %}
    </section>
  </section>
</section>
{% endblock %}

```
ZEILEN-ERKLAERUNG
1. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
2. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
3. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
4. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
5. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
6. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
7. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
8. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
9. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
10. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
11. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
12. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
13. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
14. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
15. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
16. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
17. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
18. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
19. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
20. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
21. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
22. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
23. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
24. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
25. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
26. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
27. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
28. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
29. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
30. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
31. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
32. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
33. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
34. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
35. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
36. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
37. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
38. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
39. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
40. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
41. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
42. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
43. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
44. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
45. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
46. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
47. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
48. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
49. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
50. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
51. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
52. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
53. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
54. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
55. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
56. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
57. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
58. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
59. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
60. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
61. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
62. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
63. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
64. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
65. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.

### app/templates/partials/recipe_list.html
```html
<p class="list-summary">
  {% if total > 0 %}
  {{ t("pagination.results_range", start=start_item, end=end_item, total=total) }}
  {% else %}
  {{ t("recipe.no_results") }}
  {% endif %}
</p>
<div class="cards">
  {% for entry in recipes_data %}
  {% set recipe = entry.recipe %}
  <article class="card recipe-card">
    {% set primary_image = entry.primary_image %}
    {% set display_image_url = entry.display_image_url %}
    {% set display_image_kind = entry.display_image_kind %}
    {% set has_pending_change_request = entry.has_pending_change_request %}
    {% set can_upload_direct = current_user and current_user.role == "admin" %}
    {% set can_request_change = current_user and current_user.role != "admin" %}
    {% set image_feedback_message = "" %}
    {% set image_feedback_error = "" %}
    {% include "partials/recipe_card_image.html" %}
    <a class="card-body-link" href="/recipes/{{ recipe.id }}" aria-label="{{ t('submission.open_detail') }}: {{ recipe.title }}">
      <div class="recipe-content">
        <h3 class="recipe-title">{{ recipe.title }}</h3>
        <p class="summary">{{ recipe.description }}</p>
        <div class="chip-row">
          <span class="chip">{{ recipe.category }}</span>
          <span class="chip">{{ difficulty_label(recipe.difficulty) }}</span>
          <span class="chip">{{ recipe.prep_time_minutes }} min</span>
        </div>
        <p class="rating-line">* {{ t("recipe.rating_short") }} {{ "%.2f"|format(entry.avg_rating) }} ({{ entry.review_count }})</p>
        <p class="card-cta">{{ t("submission.open_detail") }}</p>
      </div>
    </a>
  </article>
  {% endfor %}
</div>
{% if pages > 1 %}
{% set filter_query = "per_page=" ~ per_page ~ "&sort=" ~ (sort|urlencode) ~ "&title=" ~ (title|urlencode) ~ "&category=" ~ (category|urlencode) ~ "&difficulty=" ~ (difficulty|urlencode) ~ "&ingredient=" ~ (ingredient|urlencode) ~ "&image_filter=" ~ (image_filter|urlencode) %}
<div class="pagination">
  <div class="pagination-links">
    {% if page > 1 %}
    <a href="/?page={{ page - 1 }}&{{ filter_query }}" hx-get="/?page={{ page - 1 }}&{{ filter_query }}" hx-target="#recipe-list" hx-push-url="true">{{ t("pagination.previous") }}</a>
    {% else %}
    <span class="disabled">{{ t("pagination.previous") }}</span>
    {% endif %}
    {% for item in pagination_items %}
    {% if item is none %}
    <span class="ellipsis">...</span>
    {% elif item == page %}
    <span class="active">{{ item }}</span>
    {% else %}
    <a href="/?page={{ item }}&{{ filter_query }}" hx-get="/?page={{ item }}&{{ filter_query }}" hx-target="#recipe-list" hx-push-url="true">{{ item }}</a>
    {% endif %}
    {% endfor %}
    {% if page < pages %}
    <a href="/?page={{ page + 1 }}&{{ filter_query }}" hx-get="/?page={{ page + 1 }}&{{ filter_query }}" hx-target="#recipe-list" hx-push-url="true">{{ t("pagination.next") }}</a>
    {% else %}
    <span class="disabled">{{ t("pagination.next") }}</span>
    {% endif %}
  </div>
  <span class="pagination-info">{{ t("pagination.page") }} {{ page }} / {{ total_pages }}</span>
</div>
{% endif %}

```
ZEILEN-ERKLAERUNG
1. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
2. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
3. Diese Zeile gibt einen Jinja-Ausdruck dynamisch aus.
4. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
5. Diese Zeile gibt einen Jinja-Ausdruck dynamisch aus.
6. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
7. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
8. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
9. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
10. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
11. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
12. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
13. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
14. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
15. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
16. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
17. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
18. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
19. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
20. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
21. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
22. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
23. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
24. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
25. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
26. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
27. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
28. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
29. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
30. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
31. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
32. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
33. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
34. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
35. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
36. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
37. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
38. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
39. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
40. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
41. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
42. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
43. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
44. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
45. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
46. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
47. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
48. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
49. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
50. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
51. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
52. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
53. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
54. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
55. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
56. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
57. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
58. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
59. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.
60. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
61. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
62. Diese Zeile definiert ein HTML-Element fuer Struktur oder Inhalt.
63. Diese Zeile enthaelt eine Jinja-Steueranweisung fuer die Template-Logik.

### app/static/style.css
```css
﻿:root {
  --bg: #f3f6fb; --surface: #ffffff; --surface-soft: #f7fafc; --text: #0f172a; --muted: #52627a;
  --border: #d5dfeb; --primary: #0f766e; --primary-hover: #0b5f59; --primary-contrast: #ffffff;
  --focus: #2563eb; --danger: #b42318; --danger-soft: #fee4e2;
  --radius-sm: 10px; --radius: 14px; --radius-lg: 18px;
  --shadow-sm: 0 2px 12px rgba(15, 23, 42, 0.07); --shadow-md: 0 12px 28px rgba(15, 23, 42, 0.12);
  --space-1: clamp(0.25rem, 0.35vw, 0.4rem); --space-2: clamp(0.5rem, 0.6vw, 0.7rem); --space-3: clamp(0.75rem, 0.9vw, 1rem);
  --space-4: clamp(1rem, 1.25vw, 1.3rem); --space-5: clamp(1.4rem, 1.7vw, 1.8rem); --space-6: clamp(1.9rem, 2.3vw, 2.5rem);
  --container-max: 1400px;
}

* { box-sizing: border-box; }
html, body { min-height: 100%; }
html { font-size: clamp(15px, 0.22vw + 14px, 17px); scroll-behavior: smooth; }
body {
  margin: 0; color: var(--text); line-height: 1.5;
  background: radial-gradient(circle at 20% -5%, #f9fbff 0%, var(--bg) 45%);
  font-family: "Segoe UI", "Inter", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}
.container { max-width: var(--container-max); margin-inline: auto; padding: clamp(16px, 2vw, 28px); }
a { color: var(--primary); }
img { display: block; max-width: 100%; }

.skip-link {
  position: fixed; z-index: 1000; top: 8px; left: 8px; color: var(--text); background: var(--surface);
  border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 0.55rem 0.75rem;
  text-decoration: none; transform: translateY(-150%); transition: transform 0.18s ease;
}
.skip-link:focus-visible { transform: translateY(0); }

.topbar {
  position: sticky; top: 0; z-index: 40; border-bottom: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.92); backdrop-filter: blur(10px);
}
.topbar-inner {
  max-width: var(--container-max); margin-inline: auto; padding: var(--space-3) clamp(16px, 2vw, 28px);
  display: flex; align-items: center; justify-content: space-between; gap: var(--space-4);
}
.brand {
  color: var(--text); text-decoration: none; letter-spacing: -0.025em;
  font-size: clamp(1.25rem, 1.5vw, 1.42rem); font-weight: 800;
}
.main-nav { display: flex; flex-wrap: wrap; align-items: center; justify-content: flex-end; gap: var(--space-2); }
.nav-link, .btn, .lang-link { min-height: 44px; }
.nav-link {
  display: inline-flex; align-items: center; justify-content: center; padding: 0.5rem 0.8rem;
  border: 1px solid transparent; border-radius: 999px; color: #334155; text-decoration: none; font-weight: 600;
  transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}
.nav-link:hover, .nav-link:focus-visible { background: #f1f5f9; border-color: var(--border); color: var(--primary-hover); }

.lang-switch {
  display: inline-flex; align-items: center; gap: var(--space-2); padding: 0.2rem;
  border: 1px solid var(--border); border-radius: 999px; background: var(--surface);
}
.lang-label { padding-inline: var(--space-2); color: var(--muted); font-size: 0.82rem; font-weight: 700; }
.lang-links { display: inline-flex; gap: 0.2rem; }
.lang-link {
  display: inline-flex; align-items: center; justify-content: center; padding: 0.32rem 0.65rem;
  border: 1px solid transparent; border-radius: 999px; color: #334155; text-decoration: none;
  font-size: 0.82rem; font-weight: 700;
}
.lang-link:hover, .lang-link:focus-visible { border-color: var(--border); background: #f1f5f9; }
.lang-link.active, .lang-link[aria-current="page"] { border-color: var(--primary); background: var(--primary); color: var(--primary-contrast); }

h1, h2, h3, h4 { margin: 0 0 var(--space-3); line-height: 1.2; letter-spacing: -0.02em; }
h1 { font-size: clamp(1.75rem, 2.2vw, 2.35rem); }
h2 { font-size: clamp(1.35rem, 1.8vw, 1.75rem); }
h3 { font-size: clamp(1.05rem, 1.2vw, 1.2rem); }
p { margin: 0 0 var(--space-3); max-width: 70ch; }

.panel {
  margin-bottom: var(--space-5); padding: var(--space-5); border: 1px solid var(--border);
  border-radius: var(--radius-lg); background: var(--surface); box-shadow: var(--shadow-sm);
}
.narrow { max-width: 540px; }

.page-grid {
  display: grid; grid-template-columns: minmax(280px, 340px) 1fr;
  gap: clamp(16px, 2vw, 28px); align-items: start;
}
.sidebar { position: sticky; top: 86px; }
.sidebar-card {
  padding: var(--space-5); border: 1px solid var(--border); border-radius: var(--radius-lg);
  background: var(--surface); box-shadow: var(--shadow-sm);
}
.sidebar-form { display: grid; gap: var(--space-3); }
.sidebar-title { margin: 0; font-size: clamp(1.6rem, 1.9vw, 2.1rem); }
.sidebar-apply { width: 100%; margin-bottom: var(--space-1); }
.content { min-width: 0; }
.recipe-list-shell { margin-top: var(--space-1); }

.filter-grid { display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); gap: var(--space-3); align-items: end; }
.col-2 { grid-column: span 2; }
.col-3 { grid-column: span 3; }
.col-4 { grid-column: span 4; }
.col-6 { grid-column: span 6; }
.field, .grid, .stack { display: grid; gap: var(--space-2); }
.field-label { margin: 0; color: #1e293b; font-size: 0.92rem; font-weight: 700; }

input, select, textarea, button {
  width: 100%; min-height: 44px; color: var(--text); font: inherit; padding: 0.62rem 0.78rem;
  border: 1px solid var(--border); border-radius: var(--radius); background: var(--surface);
}
input::placeholder, textarea::placeholder { color: #94a3b8; }
:focus-visible { outline: 3px solid var(--focus); outline-offset: 2px; }

button {
  cursor: pointer; color: var(--primary-contrast); background: var(--primary); border-color: var(--primary); font-weight: 700;
  transition: transform 0.12s ease, background-color 0.2s ease, border-color 0.2s ease;
}
button:hover { background: var(--primary-hover); border-color: var(--primary-hover); }
button:active { transform: translateY(1px); }
button:disabled { cursor: not-allowed; opacity: 0.65; }

.btn {
  display: inline-flex; align-items: center; justify-content: center; padding: 0.55rem 0.95rem;
  border: 1px solid transparent; border-radius: 999px; font-size: 0.92rem; font-weight: 700; text-decoration: none;
}
.btn-primary { color: var(--primary-contrast); background: var(--primary); border-color: var(--primary); }
.btn-primary:hover, .btn-primary:focus-visible { color: var(--primary-contrast); background: var(--primary-hover); border-color: var(--primary-hover); }
.btn-secondary { color: #334155; background: var(--surface); border-color: var(--border); }
.btn-secondary:hover, .btn-secondary:focus-visible { color: #0f172a; background: #f8fafc; }
.inline { display: inline-flex; align-items: center; gap: var(--space-2); }
.inline input, .inline select, .inline button { width: auto; }

.list-summary { margin: 0 0 var(--space-4); color: var(--muted); font-size: 1rem; font-weight: 600; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: clamp(14px, 1.6vw, 22px); }
.recipe-card {
  padding: 0; overflow: hidden; border: 1px solid var(--border); border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm); transition: transform 0.18s ease, box-shadow 0.2s ease;
}
.recipe-card:hover, .recipe-card:focus-within { transform: translateY(-4px); box-shadow: var(--shadow-md); }

.card-image-wrap { position: relative; }
.thumb { width: 100%; height: 170px; object-fit: cover; background: #e2e8f0; }
.hero-image { width: 100%; max-height: 420px; object-fit: cover; border-radius: var(--radius-lg); margin-bottom: var(--space-4); }

.card-body-link { display: block; height: 100%; color: inherit; cursor: pointer; text-decoration: none; }
.card-body-link:focus-visible { outline: none; box-shadow: inset 0 0 0 3px rgba(37, 99, 235, 0.35); }
.recipe-content { height: 100%; display: grid; gap: var(--space-3); padding: var(--space-4); }
.recipe-title {
  margin: 0; color: var(--text); line-height: 1.35; display: -webkit-box;
  -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.card-body-link:hover .recipe-title, .card-body-link:focus-visible .recipe-title { color: var(--primary); }
.recipe-title a { color: inherit; text-decoration: none; }
.summary {
  margin: 0; color: #334155; display: -webkit-box;
  -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
}

.chip-row { display: flex; flex-wrap: wrap; gap: var(--space-2); }
.chip {
  color: #1e293b; font-size: 0.82rem; font-weight: 700; padding: 0.26rem 0.65rem;
  border: 1px solid #cdd6e3; border-radius: 999px; background: var(--surface-soft);
}
.rating-line { margin: 0; color: var(--muted); font-size: 0.92rem; font-weight: 600; }
.card-cta { margin: 0; margin-top: auto; color: var(--primary); font-size: 0.9rem; font-weight: 700; }

.placeholder-thumb, .hero-placeholder {
  position: relative; display: grid; place-items: center; color: #64748b; text-align: center;
  border: 1px dashed #94a3b8; background: linear-gradient(145deg, #f8fafc, #edf2f7);
}
.placeholder-thumb { height: 170px; }
.hero-placeholder { min-height: 320px; margin-bottom: var(--space-4); border-radius: var(--radius-lg); }
.placeholder-inner { display: grid; gap: var(--space-2); justify-items: center; padding: var(--space-4); }
.placeholder-icon {
  width: 2rem; height: 2rem; display: grid; place-items: center; color: #334155; font-size: 1.1rem; font-weight: 800;
  border: 1px solid #cbd5e1; border-radius: 999px; background: var(--surface);
}
.placeholder-label { font-size: 0.88rem; font-weight: 700; }
.placeholder-login { margin-top: var(--space-2); text-decoration: none; }

.plus-uploader {
  position: absolute; top: var(--space-2); right: var(--space-2); max-width: 88%; padding: var(--space-2);
  border: 1px solid var(--border); border-radius: var(--radius-sm); background: rgba(255, 255, 255, 0.95); box-shadow: var(--shadow-sm);
}
.plus-uploader summary {
  list-style: none; cursor: pointer; width: 2rem; height: 2rem; display: grid; place-items: center;
  color: var(--primary-contrast); font-size: 1.2rem; font-weight: 800; border-radius: 999px; background: var(--primary);
}
.plus-uploader summary::-webkit-details-marker { display: none; }
.plus-uploader[open] summary { margin-bottom: var(--space-2); }
.plus-uploader form { min-width: 220px; }
.pending-badge {
  margin: var(--space-2); display: inline-block; color: #b54708; font-size: 0.8rem; font-weight: 700; padding: 0.2rem 0.58rem;
  border: 1px solid #f7b955; border-radius: 999px; background: #fffaeb;
}

.actions { display: flex; flex-wrap: wrap; gap: var(--space-2); margin-top: var(--space-3); }
.hidden { display: none !important; }
.error {
  margin: 0; color: var(--danger); font-weight: 700; padding: 0.7rem 0.8rem;
  border: 1px solid #fda29b; border-radius: var(--radius); background: var(--danger-soft);
}
.flash {
  margin: 0 0 var(--space-4); font-size: 0.94rem; font-weight: 700; padding: 0.72rem 0.85rem;
  border: 1px solid transparent; border-radius: var(--radius);
}
.flash-success { color: #115e59; border-color: #99f6e4; background: #ecfeff; }
.flash-error { color: var(--danger); border-color: #fda29b; background: var(--danger-soft); }

.pagination { margin-top: var(--space-5); display: grid; justify-items: center; gap: var(--space-3); }
.pagination-links { display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: var(--space-2); }
.pagination-links a, .pagination-links .active, .pagination-links .disabled {
  min-width: 2.2rem; text-align: center; font-size: 0.9rem; font-weight: 700; padding: 0.36rem 0.72rem; border-radius: 999px;
}
.pagination-links a { color: #334155; text-decoration: none; border: 1px solid var(--border); background: var(--surface); }
.pagination-links a:hover, .pagination-links a:focus-visible { border-color: #b7c2d0; background: #f8fafc; }
.pagination-links .active { color: var(--primary-contrast); border: 1px solid var(--primary); background: var(--primary); }
.pagination-links .disabled { color: #94a3b8; border: 1px solid #e2e8f0; background: #f8fafc; }
.pagination-links .ellipsis { color: var(--muted); font-weight: 700; padding: 0 0.28rem; }
.pagination-info { color: var(--muted); font-size: 0.92rem; font-weight: 600; }

.meta, .muted { margin: 0; color: var(--muted); font-size: 0.92rem; }
pre {
  margin: 0; padding: var(--space-3); white-space: pre-wrap; word-break: break-word;
  border: 1px solid var(--border); border-radius: var(--radius); background: #f8fafc;
}

table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; vertical-align: top; padding: 0.64rem 0.45rem; border-bottom: 1px solid #e2e8f0; }

@media (max-width: 1080px) {
  .topbar-inner { flex-direction: column; align-items: flex-start; }
  .main-nav { width: 100%; justify-content: flex-start; }
}

@media (max-width: 980px) {
  .page-grid { grid-template-columns: 1fr; }
  .sidebar { position: static; }
  .col-2, .col-3, .col-4, .col-6 { grid-column: span 6; }
}

@media (max-width: 760px) {
  .panel, .sidebar-card { padding: var(--space-4); }
  .cards { grid-template-columns: 1fr; }
  .filter-grid { grid-template-columns: 1fr; }
  .col-2, .col-3, .col-4, .col-6 { grid-column: auto; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important; animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important; scroll-behavior: auto !important;
  }
  .recipe-card:hover, .recipe-card:focus-within { transform: none; }
}

```
ZEILEN-ERKLAERUNG
1. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
2. Diese Zeile setzt eine CSS-Variable als Design-Token.
3. Diese Zeile setzt eine CSS-Variable als Design-Token.
4. Diese Zeile setzt eine CSS-Variable als Design-Token.
5. Diese Zeile setzt eine CSS-Variable als Design-Token.
6. Diese Zeile setzt eine CSS-Variable als Design-Token.
7. Diese Zeile setzt eine CSS-Variable als Design-Token.
8. Diese Zeile setzt eine CSS-Variable als Design-Token.
9. Diese Zeile setzt eine CSS-Variable als Design-Token.
10. Diese Zeile schliesst den aktuellen Block korrekt ab.
11. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
12. Diese Zeile adressiert einen globalen Selektor fuer einheitliches Verhalten.
13. Diese Zeile unterstuetzt die technische Struktur der Datei.
14. Diese Zeile unterstuetzt die technische Struktur der Datei.
15. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
16. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
17. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
18. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
19. Diese Zeile schliesst den aktuellen Block korrekt ab.
20. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
21. Diese Zeile unterstuetzt die technische Struktur der Datei.
22. Diese Zeile unterstuetzt die technische Struktur der Datei.
23. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
24. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
25. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
26. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
27. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
28. Diese Zeile schliesst den aktuellen Block korrekt ab.
29. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
30. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
31. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
32. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
33. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
34. Diese Zeile schliesst den aktuellen Block korrekt ab.
35. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
36. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
37. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
38. Diese Zeile schliesst den aktuellen Block korrekt ab.
39. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
40. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
41. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
42. Diese Zeile schliesst den aktuellen Block korrekt ab.
43. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
44. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
45. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
46. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
47. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
48. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
49. Diese Zeile schliesst den aktuellen Block korrekt ab.
50. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
51. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
52. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
53. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
54. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
55. Diese Zeile schliesst den aktuellen Block korrekt ab.
56. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
57. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
58. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
59. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
60. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
61. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
62. Diese Zeile schliesst den aktuellen Block korrekt ab.
63. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
64. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
65. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
66. Diese Zeile unterstuetzt die technische Struktur der Datei.
67. Diese Zeile unterstuetzt die technische Struktur der Datei.
68. Diese Zeile unterstuetzt die technische Struktur der Datei.
69. Diese Zeile unterstuetzt die technische Struktur der Datei.
70. Diese Zeile unterstuetzt die technische Struktur der Datei.
71. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
72. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
73. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
74. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
75. Diese Zeile schliesst den aktuellen Block korrekt ab.
76. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
77. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
78. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
79. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
80. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
81. Diese Zeile schliesst den aktuellen Block korrekt ab.
82. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
83. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
84. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
85. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
86. Diese Zeile schliesst den aktuellen Block korrekt ab.
87. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
88. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
89. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
90. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
91. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
92. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
93. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
94. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
95. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
96. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
97. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
98. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
99. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
100. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
101. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
102. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
103. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
104. Diese Zeile schliesst den aktuellen Block korrekt ab.
105. Diese Zeile unterstuetzt die technische Struktur der Datei.
106. Diese Zeile unterstuetzt die technische Struktur der Datei.
107. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
108. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
109. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
110. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
111. Diese Zeile schliesst den aktuellen Block korrekt ab.
112. Diese Zeile unterstuetzt die technische Struktur der Datei.
113. Diese Zeile unterstuetzt die technische Struktur der Datei.
114. Diese Zeile unterstuetzt die technische Struktur der Datei.
115. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
116. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
117. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
118. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
119. Diese Zeile schliesst den aktuellen Block korrekt ab.
120. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
121. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
122. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
123. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
124. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
125. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
126. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
127. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
128. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
129. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
130. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
131. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
132. Diese Zeile schliesst den aktuellen Block korrekt ab.
133. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
134. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
135. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
136. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
137. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
138. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
139. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
140. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
141. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
142. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
143. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
144. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
145. Diese Zeile schliesst den aktuellen Block korrekt ab.
146. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
147. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
148. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
149. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
150. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
151. Diese Zeile schliesst den aktuellen Block korrekt ab.
152. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
153. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
154. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
155. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
156. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
157. Diese Zeile schliesst den aktuellen Block korrekt ab.
158. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
159. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
160. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
161. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
162. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
163. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
164. Diese Zeile schliesst den aktuellen Block korrekt ab.
165. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
166. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
167. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
168. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
169. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
170. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
171. Diese Zeile schliesst den aktuellen Block korrekt ab.
172. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
173. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
174. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
175. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
176. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
177. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
178. Diese Zeile schliesst den aktuellen Block korrekt ab.
179. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
180. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
181. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
182. Diese Zeile schliesst den aktuellen Block korrekt ab.
183. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
184. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
185. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
186. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
187. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
188. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
189. Diese Zeile schliesst den aktuellen Block korrekt ab.
190. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
191. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
192. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
193. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
194. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
195. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
196. Diese Zeile schliesst den aktuellen Block korrekt ab.
197. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
198. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
199. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
200. Diese Zeile schliesst den aktuellen Block korrekt ab.
201. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
202. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
203. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
204. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
205. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
206. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
207. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
208. Diese Zeile schliesst den aktuellen Block korrekt ab.
209. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
210. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
211. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
212. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
213. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
214. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
215. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
216. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
217. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
218. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
219. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
220. Diese Zeile schliesst den aktuellen Block korrekt ab.
221. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
222. Diese Zeile unterstuetzt die technische Struktur der Datei.
223. Diese Zeile unterstuetzt die technische Struktur der Datei.
224. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
225. Diese Zeile startet eine Media-Query fuer Responsive- oder Accessibility-Verhalten.
226. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
227. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
228. Diese Zeile schliesst den aktuellen Block korrekt ab.
229. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
230. Diese Zeile startet eine Media-Query fuer Responsive- oder Accessibility-Verhalten.
231. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
232. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
233. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
234. Diese Zeile schliesst den aktuellen Block korrekt ab.
235. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
236. Diese Zeile startet eine Media-Query fuer Responsive- oder Accessibility-Verhalten.
237. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
238. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
239. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
240. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
241. Diese Zeile schliesst den aktuellen Block korrekt ab.
242. Diese Zeile ist eine Leerzeile fuer bessere Lesbarkeit.
243. Diese Zeile startet eine Media-Query fuer Responsive- oder Accessibility-Verhalten.
244. Diese Zeile oeffnet einen CSS-Selektorblock fuer folgende Regeln.
245. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
246. Diese Zeile setzt eine konkrete CSS-Eigenschaft fuer das Layout oder Styling.
247. Diese Zeile schliesst den aktuellen Block korrekt ab.
248. Diese Zeile benennt einen CSS-Selektor fuer eine bestimmte Komponente.
249. Diese Zeile schliesst den aktuellen Block korrekt ab.