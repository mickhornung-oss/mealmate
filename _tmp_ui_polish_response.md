Ge?nderte Dateien: `app/templates/base.html`, `app/templates/home.html`, `app/templates/partials/recipe_list.html`, `app/static/style.css`.

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
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
2. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
3. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
4. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
5. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
6. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
7. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
8. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
9. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
10. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
11. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
12. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
13. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
14. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
15. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
16. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
17. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
18. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
19. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
20. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
21. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
22. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
23. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
24. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
25. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
26. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
27. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
28. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
29. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
30. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
31. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
32. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
33. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
34. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
35. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
36. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
37. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
38. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
39. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
40. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
41. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
42. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
43. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
44. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
45. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
46. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
47. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
48. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
49. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
50. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
51. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
52. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
53. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
54. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
55. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
56. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
57. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
58. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
59. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
60. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.

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
ZEILEN-ERKL?RUNG
1. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
2. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
3. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
4. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
5. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
6. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
7. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
8. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
9. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
10. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
11. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
12. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
13. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
14. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
15. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
16. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
17. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
18. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
19. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
20. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
21. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
22. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
23. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
24. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
25. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
26. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
27. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
28. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
29. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
30. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
31. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
32. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
33. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
34. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
35. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
36. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
37. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
38. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
39. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
40. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
41. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
42. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
43. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
44. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
45. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
46. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
47. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
48. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
49. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
50. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
51. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
52. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
53. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
54. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
55. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
56. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
57. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
58. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
59. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
60. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
61. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
62. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
63. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
64. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
65. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.

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
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
2. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
3. Diese Zeile gibt einen Jinja-Ausdruck dynamisch im Template aus.
4. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
5. Diese Zeile gibt einen Jinja-Ausdruck dynamisch im Template aus.
6. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
7. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
8. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
9. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
10. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
11. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
12. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
13. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
14. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
15. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
16. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
17. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
18. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
19. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
20. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
21. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
22. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
23. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
24. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
25. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
26. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
27. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
28. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
29. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
30. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
31. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
32. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
33. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
34. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
35. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
36. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
37. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
38. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
39. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
40. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
41. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
42. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
43. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
44. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
45. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
46. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
47. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
48. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
49. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
50. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
51. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
52. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
53. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
54. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
55. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
56. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
57. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
58. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
59. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.
60. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
61. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
62. Diese Zeile definiert ein HTML-Element f?r Struktur oder Inhalt der Seite.
63. Diese Zeile enth?lt eine Jinja-Steueranweisung f?r die Template-Logik.

### app/static/style.css
```css
﻿:root {
  --bg: #f4f7fb;
  --surface: #ffffff;
  --surface-soft: #f8fafc;
  --text: #0f172a;
  --muted: #475569;
  --border: #d7dee8;
  --primary: #0f766e;
  --primary-hover: #0c5f59;
  --primary-contrast: #ffffff;
  --focus: #2563eb;
  --danger: #b42318;
  --danger-soft: #fee4e2;
  --radius-sm: 10px;
  --radius: 14px;
  --radius-lg: 18px;
  --shadow-sm: 0 2px 10px rgba(15, 23, 42, 0.06);
  --shadow-md: 0 12px 26px rgba(15, 23, 42, 0.1);
  --space-1: clamp(0.25rem, 0.35vw, 0.4rem);
  --space-2: clamp(0.5rem, 0.6vw, 0.7rem);
  --space-3: clamp(0.75rem, 0.9vw, 1rem);
  --space-4: clamp(1rem, 1.25vw, 1.3rem);
  --space-5: clamp(1.4rem, 1.7vw, 1.8rem);
  --space-6: clamp(1.9rem, 2.3vw, 2.5rem);
  --container-max: 1400px;
}

* {
  box-sizing: border-box;
}

html,
body {
  min-height: 100%;
}

html {
  font-size: clamp(15px, 0.22vw + 14px, 17px);
  scroll-behavior: smooth;
}

body {
  margin: 0;
  background: radial-gradient(circle at 20% -5%, #f8fbff 0%, var(--bg) 45%);
  color: var(--text);
  font-family: "Inter", "Segoe UI", system-ui, -apple-system, sans-serif;
  line-height: 1.5;
}

a {
  color: var(--primary);
}

img {
  display: block;
  max-width: 100%;
}

.skip-link {
  position: fixed;
  z-index: 1000;
  top: 8px;
  left: 8px;
  border-radius: var(--radius-sm);
  background: var(--surface);
  border: 1px solid var(--border);
  padding: 0.55rem 0.75rem;
  color: var(--text);
  text-decoration: none;
  transform: translateY(-150%);
  transition: transform 0.18s ease;
}

.skip-link:focus-visible {
  transform: translateY(0);
}

.container {
  max-width: var(--container-max);
  margin-inline: auto;
  padding: clamp(16px, 2vw, 28px);
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 40;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border);
}

.topbar-inner {
  max-width: var(--container-max);
  margin-inline: auto;
  padding: var(--space-3) clamp(16px, 2vw, 28px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
}

.brand {
  color: var(--text);
  text-decoration: none;
  font-size: clamp(1.25rem, 1.5vw, 1.42rem);
  font-weight: 800;
  letter-spacing: -0.025em;
}

.main-nav {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: var(--space-2);
}

.nav-link,
.btn,
.lang-link {
  min-height: 44px;
}

.nav-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 0.8rem;
  border-radius: 999px;
  border: 1px solid transparent;
  color: #334155;
  text-decoration: none;
  font-weight: 600;
  transition: background-color 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.nav-link:hover,
.nav-link:focus-visible {
  background: #f1f5f9;
  border-color: var(--border);
  color: var(--primary-hover);
}

.lang-switch {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--surface);
  padding: 0.2rem;
}

.lang-label {
  padding-inline: var(--space-2);
  color: var(--muted);
  font-size: 0.82rem;
  font-weight: 700;
}

.lang-links {
  display: inline-flex;
  gap: 0.2rem;
}

.lang-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.32rem 0.65rem;
  border-radius: 999px;
  border: 1px solid transparent;
  color: #334155;
  text-decoration: none;
  font-size: 0.82rem;
  font-weight: 700;
}

.lang-link:hover,
.lang-link:focus-visible {
  border-color: var(--border);
  background: #f1f5f9;
}

.lang-link.active,
.lang-link[aria-current="page"] {
  border-color: var(--primary);
  background: var(--primary);
  color: var(--primary-contrast);
}

h1,
h2,
h3,
h4 {
  margin: 0 0 var(--space-3);
  line-height: 1.2;
  letter-spacing: -0.02em;
}

h1 {
  font-size: clamp(1.75rem, 2.2vw, 2.35rem);
}

h2 {
  font-size: clamp(1.35rem, 1.8vw, 1.75rem);
}

h3 {
  font-size: clamp(1.05rem, 1.2vw, 1.2rem);
}

p {
  margin: 0 0 var(--space-3);
  max-width: 70ch;
}

.panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: var(--space-5);
  margin-bottom: var(--space-5);
}

.narrow {
  max-width: 540px;
}

.page-grid {
  display: grid;
  grid-template-columns: minmax(280px, 340px) 1fr;
  gap: clamp(16px, 2vw, 28px);
  align-items: start;
}

.sidebar {
  position: sticky;
  top: 86px;
}

.sidebar-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: var(--space-5);
}

.sidebar-form {
  display: grid;
  gap: var(--space-3);
}

.sidebar-title {
  margin: 0;
  font-size: clamp(1.6rem, 1.9vw, 2.1rem);
}

.sidebar-apply {
  width: 100%;
  margin-bottom: var(--space-1);
}

.content {
  min-width: 0;
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: var(--space-3);
  align-items: end;
}

.col-2 {
  grid-column: span 2;
}

.col-3 {
  grid-column: span 3;
}

.col-4 {
  grid-column: span 4;
}

.col-6 {
  grid-column: span 6;
}

.field {
  display: grid;
  gap: var(--space-2);
}

.field-label {
  margin: 0;
  color: #1e293b;
  font-weight: 700;
  font-size: 0.92rem;
}

.grid {
  display: grid;
  gap: var(--space-3);
}

.stack {
  display: grid;
  gap: var(--space-3);
}

input,
select,
textarea,
button {
  width: 100%;
  min-height: 44px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.62rem 0.78rem;
  font: inherit;
  color: var(--text);
  background: var(--surface);
}

input::placeholder,
textarea::placeholder {
  color: #94a3b8;
}

:focus-visible {
  outline: 3px solid var(--focus);
  outline-offset: 2px;
}

button {
  cursor: pointer;
  color: var(--primary-contrast);
  background: var(--primary);
  border-color: var(--primary);
  font-weight: 700;
  transition: transform 0.12s ease, background-color 0.2s ease, border-color 0.2s ease;
}

button:hover {
  background: var(--primary-hover);
  border-color: var(--primary-hover);
}

button:active {
  transform: translateY(1px);
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  border: 1px solid transparent;
  padding: 0.55rem 0.95rem;
  text-decoration: none;
  font-size: 0.92rem;
  font-weight: 700;
}

.btn-primary {
  background: var(--primary);
  border-color: var(--primary);
  color: var(--primary-contrast);
}

.btn-primary:hover,
.btn-primary:focus-visible {
  background: var(--primary-hover);
  border-color: var(--primary-hover);
  color: var(--primary-contrast);
}

.btn-secondary {
  color: #334155;
  border-color: var(--border);
  background: var(--surface);
}

.btn-secondary:hover,
.btn-secondary:focus-visible {
  background: #f8fafc;
  color: #0f172a;
}

.inline {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
}

.inline input,
.inline select,
.inline button {
  width: auto;
}

.recipe-list-shell {
  margin-top: var(--space-1);
}

.list-summary {
  margin: 0 0 var(--space-4);
  color: var(--muted);
  font-size: 1rem;
  font-weight: 600;
}

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: clamp(14px, 1.6vw, 22px);
}

.recipe-card {
  padding: 0;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: transform 0.18s ease, box-shadow 0.2s ease;
}

.recipe-card:hover,
.recipe-card:focus-within {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.card-image-wrap {
  position: relative;
}

.thumb {
  width: 100%;
  height: 170px;
  object-fit: cover;
  background: #e2e8f0;
}

.hero-image {
  width: 100%;
  max-height: 420px;
  object-fit: cover;
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-4);
}

.card-body-link {
  display: block;
  color: inherit;
  text-decoration: none;
  cursor: pointer;
  height: 100%;
}

.card-body-link:focus-visible {
  outline: none;
  box-shadow: inset 0 0 0 3px rgba(37, 99, 235, 0.35);
}

.recipe-content {
  display: grid;
  gap: var(--space-3);
  padding: var(--space-4);
  height: 100%;
}

.recipe-title {
  margin: 0;
  color: var(--text);
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-body-link:hover .recipe-title,
.card-body-link:focus-visible .recipe-title {
  color: var(--primary);
}

.recipe-title a {
  color: inherit;
  text-decoration: none;
}

.summary {
  margin: 0;
  color: #334155;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.chip {
  border: 1px solid #cdd6e3;
  border-radius: 999px;
  background: var(--surface-soft);
  color: #1e293b;
  font-size: 0.82rem;
  font-weight: 700;
  padding: 0.26rem 0.65rem;
}

.rating-line {
  margin: 0;
  color: var(--muted);
  font-size: 0.92rem;
  font-weight: 600;
}

.card-cta {
  margin: 0;
  margin-top: auto;
  color: var(--primary);
  font-size: 0.9rem;
  font-weight: 700;
}

.placeholder-thumb,
.hero-placeholder {
  display: grid;
  place-items: center;
  border: 1px dashed #94a3b8;
  background: linear-gradient(145deg, #f8fafc, #edf2f7);
  color: #64748b;
  text-align: center;
  position: relative;
}

.placeholder-thumb {
  height: 170px;
}

.hero-placeholder {
  min-height: 320px;
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-4);
}

.placeholder-inner {
  display: grid;
  gap: var(--space-2);
  justify-items: center;
  padding: var(--space-4);
}

.placeholder-icon {
  width: 2rem;
  height: 2rem;
  display: grid;
  place-items: center;
  border-radius: 999px;
  border: 1px solid #cbd5e1;
  background: var(--surface);
  color: #334155;
  font-size: 1.1rem;
  font-weight: 800;
}

.placeholder-label {
  font-size: 0.88rem;
  font-weight: 700;
}

.plus-uploader {
  position: absolute;
  top: var(--space-2);
  right: var(--space-2);
  max-width: 88%;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.95);
  box-shadow: var(--shadow-sm);
  padding: var(--space-2);
}

.plus-uploader summary {
  list-style: none;
  cursor: pointer;
  width: 2rem;
  height: 2rem;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: var(--primary);
  color: var(--primary-contrast);
  font-size: 1.2rem;
  font-weight: 800;
}

.plus-uploader summary::-webkit-details-marker {
  display: none;
}

.plus-uploader[open] summary {
  margin-bottom: var(--space-2);
}

.plus-uploader form {
  min-width: 220px;
}

.pending-badge {
  margin: var(--space-2);
  display: inline-block;
  border: 1px solid #f7b955;
  border-radius: 999px;
  background: #fffaeb;
  color: #b54708;
  font-size: 0.8rem;
  font-weight: 700;
  padding: 0.2rem 0.58rem;
}

.placeholder-login {
  text-decoration: none;
  margin-top: var(--space-2);
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-top: var(--space-3);
}

.hidden {
  display: none !important;
}

.error {
  margin: 0;
  border: 1px solid #fda29b;
  border-radius: var(--radius);
  background: var(--danger-soft);
  color: var(--danger);
  font-weight: 700;
  padding: 0.7rem 0.8rem;
}

.flash {
  margin: 0 0 var(--space-4);
  border-radius: var(--radius);
  border: 1px solid transparent;
  padding: 0.72rem 0.85rem;
  font-size: 0.94rem;
  font-weight: 700;
}

.flash-success {
  border-color: #99f6e4;
  background: #ecfeff;
  color: #115e59;
}

.flash-error {
  border-color: #fda29b;
  background: var(--danger-soft);
  color: var(--danger);
}

.pagination {
  margin-top: var(--space-5);
  display: grid;
  justify-items: center;
  gap: var(--space-3);
}

.pagination-links {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
}

.pagination-links a,
.pagination-links .active,
.pagination-links .disabled {
  min-width: 2.2rem;
  border-radius: 999px;
  text-align: center;
  font-size: 0.9rem;
  font-weight: 700;
  padding: 0.36rem 0.72rem;
}

.pagination-links a {
  border: 1px solid var(--border);
  background: var(--surface);
  color: #334155;
  text-decoration: none;
}

.pagination-links a:hover,
.pagination-links a:focus-visible {
  border-color: #b7c2d0;
  background: #f8fafc;
}

.pagination-links .active {
  border: 1px solid var(--primary);
  background: var(--primary);
  color: var(--primary-contrast);
}

.pagination-links .disabled {
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #94a3b8;
}

.pagination-links .ellipsis {
  color: var(--muted);
  font-weight: 700;
  padding: 0 0.28rem;
}

.pagination-info {
  color: var(--muted);
  font-size: 0.92rem;
  font-weight: 600;
}

.meta,
.muted {
  margin: 0;
  color: var(--muted);
  font-size: 0.92rem;
}

pre {
  margin: 0;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: #f8fafc;
  white-space: pre-wrap;
  word-break: break-word;
  padding: var(--space-3);
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  border-bottom: 1px solid #e2e8f0;
  text-align: left;
  padding: 0.64rem 0.45rem;
  vertical-align: top;
}

@media (max-width: 1080px) {
  .topbar-inner {
    align-items: flex-start;
    flex-direction: column;
  }

  .main-nav {
    width: 100%;
    justify-content: flex-start;
  }
}

@media (max-width: 980px) {
  .page-grid {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: static;
  }

  .col-2,
  .col-3,
  .col-4,
  .col-6 {
    grid-column: span 6;
  }
}

@media (max-width: 760px) {
  .panel,
  .sidebar-card {
    padding: var(--space-4);
  }

  .cards {
    grid-template-columns: 1fr;
  }

  .filter-grid {
    grid-template-columns: 1fr;
  }

  .col-2,
  .col-3,
  .col-4,
  .col-6 {
    grid-column: auto;
  }
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }

  .recipe-card:hover,
  .recipe-card:focus-within {
    transform: none;
  }
}

```
ZEILEN-ERKL?RUNG
1. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
2. Diese Zeile definiert ein CSS-Design-Token als Variable.
3. Diese Zeile definiert ein CSS-Design-Token als Variable.
4. Diese Zeile definiert ein CSS-Design-Token als Variable.
5. Diese Zeile definiert ein CSS-Design-Token als Variable.
6. Diese Zeile definiert ein CSS-Design-Token als Variable.
7. Diese Zeile definiert ein CSS-Design-Token als Variable.
8. Diese Zeile definiert ein CSS-Design-Token als Variable.
9. Diese Zeile definiert ein CSS-Design-Token als Variable.
10. Diese Zeile definiert ein CSS-Design-Token als Variable.
11. Diese Zeile definiert ein CSS-Design-Token als Variable.
12. Diese Zeile definiert ein CSS-Design-Token als Variable.
13. Diese Zeile definiert ein CSS-Design-Token als Variable.
14. Diese Zeile definiert ein CSS-Design-Token als Variable.
15. Diese Zeile definiert ein CSS-Design-Token als Variable.
16. Diese Zeile definiert ein CSS-Design-Token als Variable.
17. Diese Zeile definiert ein CSS-Design-Token als Variable.
18. Diese Zeile definiert ein CSS-Design-Token als Variable.
19. Diese Zeile definiert ein CSS-Design-Token als Variable.
20. Diese Zeile definiert ein CSS-Design-Token als Variable.
21. Diese Zeile definiert ein CSS-Design-Token als Variable.
22. Diese Zeile definiert ein CSS-Design-Token als Variable.
23. Diese Zeile definiert ein CSS-Design-Token als Variable.
24. Diese Zeile definiert ein CSS-Design-Token als Variable.
25. Diese Zeile definiert ein CSS-Design-Token als Variable.
26. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
27. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
28. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
29. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
30. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
31. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
32. Diese Zeile geh?rt zur technischen Struktur und unterst?tzt die Gesamtfunktion der Datei.
33. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
34. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
35. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
36. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
37. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
38. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
39. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
40. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
41. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
42. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
43. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
44. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
45. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
46. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
47. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
48. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
49. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
50. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
51. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
52. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
53. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
54. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
55. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
56. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
57. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
58. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
59. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
60. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
61. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
62. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
63. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
64. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
65. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
66. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
67. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
68. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
69. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
70. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
71. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
72. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
73. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
74. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
75. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
76. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
77. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
78. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
79. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
80. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
81. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
82. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
83. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
84. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
85. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
86. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
87. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
88. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
89. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
90. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
91. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
92. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
93. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
94. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
95. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
96. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
97. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
98. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
99. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
100. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
101. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
102. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
103. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
104. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
105. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
106. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
107. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
108. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
109. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
110. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
111. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
112. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
113. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
114. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
115. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
116. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
117. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
118. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
119. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
120. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
121. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
122. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
123. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
124. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
125. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
126. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
127. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
128. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
129. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
130. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
131. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
132. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
133. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
134. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
135. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
136. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
137. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
138. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
139. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
140. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
141. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
142. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
143. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
144. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
145. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
146. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
147. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
148. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
149. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
150. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
151. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
152. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
153. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
154. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
155. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
156. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
157. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
158. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
159. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
160. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
161. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
162. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
163. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
164. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
165. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
166. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
167. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
168. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
169. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
170. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
171. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
172. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
173. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
174. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
175. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
176. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
177. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
178. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
179. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
180. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
181. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
182. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
183. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
184. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
185. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
186. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
187. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
188. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
189. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
190. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
191. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
192. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
193. Diese Zeile geh?rt zur technischen Struktur und unterst?tzt die Gesamtfunktion der Datei.
194. Diese Zeile geh?rt zur technischen Struktur und unterst?tzt die Gesamtfunktion der Datei.
195. Diese Zeile geh?rt zur technischen Struktur und unterst?tzt die Gesamtfunktion der Datei.
196. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
197. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
198. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
199. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
200. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
201. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
202. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
203. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
204. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
205. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
206. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
207. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
208. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
209. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
210. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
211. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
212. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
213. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
214. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
215. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
216. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
217. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
218. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
219. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
220. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
221. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
222. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
223. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
224. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
225. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
226. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
227. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
228. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
229. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
230. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
231. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
232. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
233. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
234. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
235. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
236. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
237. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
238. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
239. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
240. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
241. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
242. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
243. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
244. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
245. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
246. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
247. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
248. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
249. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
250. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
251. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
252. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
253. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
254. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
255. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
256. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
257. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
258. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
259. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
260. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
261. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
262. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
263. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
264. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
265. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
266. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
267. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
268. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
269. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
270. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
271. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
272. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
273. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
274. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
275. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
276. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
277. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
278. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
279. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
280. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
281. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
282. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
283. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
284. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
285. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
286. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
287. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
288. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
289. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
290. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
291. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
292. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
293. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
294. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
295. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
296. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
297. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
298. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
299. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
300. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
301. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
302. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
303. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
304. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
305. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
306. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
307. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
308. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
309. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
310. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
311. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
312. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
313. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
314. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
315. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
316. Diese Zeile geh?rt zur technischen Struktur und unterst?tzt die Gesamtfunktion der Datei.
317. Diese Zeile geh?rt zur technischen Struktur und unterst?tzt die Gesamtfunktion der Datei.
318. Diese Zeile geh?rt zur technischen Struktur und unterst?tzt die Gesamtfunktion der Datei.
319. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
320. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
321. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
322. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
323. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
324. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
325. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
326. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
327. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
328. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
329. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
330. Diese Zeile geh?rt zur technischen Struktur und unterst?tzt die Gesamtfunktion der Datei.
331. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
332. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
333. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
334. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
335. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
336. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
337. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
338. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
339. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
340. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
341. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
342. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
343. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
344. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
345. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
346. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
347. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
348. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
349. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
350. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
351. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
352. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
353. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
354. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
355. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
356. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
357. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
358. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
359. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
360. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
361. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
362. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
363. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
364. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
365. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
366. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
367. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
368. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
369. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
370. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
371. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
372. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
373. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
374. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
375. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
376. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
377. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
378. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
379. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
380. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
381. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
382. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
383. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
384. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
385. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
386. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
387. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
388. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
389. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
390. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
391. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
392. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
393. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
394. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
395. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
396. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
397. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
398. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
399. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
400. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
401. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
402. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
403. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
404. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
405. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
406. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
407. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
408. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
409. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
410. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
411. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
412. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
413. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
414. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
415. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
416. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
417. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
418. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
419. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
420. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
421. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
422. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
423. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
424. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
425. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
426. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
427. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
428. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
429. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
430. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
431. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
432. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
433. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
434. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
435. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
436. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
437. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
438. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
439. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
440. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
441. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
442. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
443. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
444. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
445. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
446. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
447. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
448. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
449. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
450. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
451. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
452. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
453. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
454. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
455. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
456. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
457. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
458. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
459. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
460. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
461. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
462. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
463. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
464. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
465. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
466. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
467. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
468. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
469. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
470. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
471. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
472. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
473. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
474. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
475. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
476. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
477. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
478. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
479. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
480. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
481. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
482. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
483. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
484. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
485. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
486. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
487. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
488. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
489. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
490. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
491. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
492. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
493. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
494. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
495. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
496. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
497. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
498. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
499. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
500. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
501. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
502. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
503. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
504. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
505. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
506. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
507. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
508. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
509. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
510. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
511. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
512. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
513. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
514. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
515. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
516. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
517. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
518. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
519. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
520. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
521. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
522. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
523. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
524. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
525. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
526. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
527. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
528. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
529. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
530. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
531. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
532. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
533. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
534. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
535. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
536. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
537. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
538. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
539. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
540. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
541. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
542. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
543. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
544. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
545. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
546. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
547. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
548. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
549. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
550. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
551. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
552. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
553. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
554. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
555. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
556. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
557. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
558. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
559. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
560. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
561. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
562. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
563. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
564. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
565. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
566. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
567. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
568. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
569. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
570. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
571. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
572. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
573. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
574. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
575. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
576. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
577. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
578. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
579. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
580. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
581. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
582. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
583. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
584. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
585. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
586. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
587. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
588. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
589. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
590. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
591. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
592. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
593. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
594. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
595. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
596. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
597. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
598. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
599. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
600. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
601. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
602. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
603. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
604. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
605. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
606. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
607. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
608. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
609. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
610. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
611. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
612. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
613. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
614. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
615. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
616. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
617. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
618. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
619. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
620. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
621. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
622. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
623. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
624. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
625. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
626. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
627. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
628. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
629. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
630. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
631. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
632. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
633. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
634. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
635. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
636. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
637. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
638. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
639. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
640. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
641. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
642. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
643. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
644. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
645. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
646. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
647. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
648. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
649. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
650. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
651. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
652. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
653. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
654. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
655. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
656. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
657. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
658. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
659. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
660. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
661. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
662. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
663. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
664. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
665. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
666. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
667. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
668. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
669. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
670. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
671. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
672. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
673. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
674. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
675. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
676. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
677. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
678. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
679. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
680. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
681. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
682. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
683. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
684. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
685. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
686. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
687. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
688. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
689. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
690. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
691. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
692. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
693. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
694. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
695. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
696. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
697. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
698. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
699. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
700. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
701. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
702. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
703. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
704. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
705. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
706. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
707. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
708. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
709. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
710. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
711. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
712. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
713. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
714. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
715. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
716. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
717. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
718. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
719. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
720. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
721. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
722. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
723. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
724. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
725. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
726. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
727. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
728. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
729. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
730. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
731. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
732. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
733. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
734. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
735. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
736. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
737. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
738. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
739. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
740. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
741. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
742. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
743. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
744. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
745. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
746. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
747. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
748. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
749. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
750. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
751. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
752. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
753. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
754. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
755. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
756. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
757. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
758. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
759. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
760. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
761. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
762. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
763. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
764. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
765. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
766. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
767. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
768. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
769. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
770. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
771. Diese Zeile geh?rt zur technischen Struktur und unterst?tzt die Gesamtfunktion der Datei.
772. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
773. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
774. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
775. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
776. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
777. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
778. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
779. Diese Zeile startet eine Media-Query f?r responsives Verhalten oder Zug?nglichkeit.
780. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
781. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
782. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
783. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
784. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
785. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
786. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
787. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
788. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
789. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
790. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
791. Diese Zeile startet eine Media-Query f?r responsives Verhalten oder Zug?nglichkeit.
792. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
793. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
794. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
795. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
796. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
797. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
798. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
799. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
800. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
801. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
802. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
803. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
804. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
805. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
806. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
807. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
808. Diese Zeile startet eine Media-Query f?r responsives Verhalten oder Zug?nglichkeit.
809. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
810. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
811. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
812. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
813. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
814. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
815. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
816. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
817. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
818. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
819. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
820. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
821. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
822. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
823. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
824. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
825. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
826. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
827. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
828. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
829. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
830. Diese Zeile startet eine Media-Query f?r responsives Verhalten oder Zug?nglichkeit.
831. Diese Zeile adressiert einen globalen CSS-Selektor f?r einheitliches Styling.
832. Diese Zeile adressiert einen globalen CSS-Selektor f?r einheitliches Styling.
833. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
834. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
835. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
836. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
837. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
838. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
839. Diese Zeile ist als Leerzeile f?r bessere Lesbarkeit eingef?gt.
840. Diese Zeile benennt einen CSS-Selektor f?r eine spezifische UI-Komponente.
841. Diese Zeile ?ffnet einen CSS-Selektorblock f?r nachfolgende Regeln.
842. Diese Zeile setzt eine konkrete CSS-Eigenschaft f?r Darstellung und Verhalten.
843. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.
844. Diese Zeile schlie?t den aktuellen CSS- oder Template-Block korrekt ab.