def test_language_default_is_de(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Rezepte entdecken" in response.text


def test_language_query_param_sets_cookie(client):
    response = client.get("/?lang=en")
    assert response.status_code == 200
    assert "Discover Recipes" in response.text
    assert response.cookies.get("lang") == "en"


def test_accept_language_header_de_picks_de(client):
    response = client.get("/", headers={"Accept-Language": "de-DE,de;q=0.9,en;q=0.8"})
    assert response.status_code == 200
    assert "Rezepte entdecken" in response.text


def test_template_renders_translation_key(client):
    response = client.get("/?lang=fr")
    assert response.status_code == 200
    assert "Decouvrir des recettes" in response.text
