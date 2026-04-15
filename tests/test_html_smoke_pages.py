from __future__ import annotations


def test_home_page_renders_recipe_list_container(client):
    response = client.get("/")
    assert response.status_code == 200
    assert 'id="recipe-list"' in response.text


def test_login_page_is_reachable(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_submit_page_is_reachable(client):
    response = client.get("/submit")
    assert response.status_code == 200


def test_admin_submissions_requires_admin(client):
    response = client.get("/admin/submissions", follow_redirects=False)
    assert response.status_code in {302, 303, 401, 403}
    location = response.headers.get("location", "")
    if response.status_code in {302, 303}:
        assert "/login" in location or location == "/"
