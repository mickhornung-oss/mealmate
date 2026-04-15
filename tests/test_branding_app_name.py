def test_home_uses_new_branding(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Kitchen Hell and Heaven" in response.text
    assert "MealMate" not in response.text


def test_footer_legal_pages_available(client):
    impressum = client.get("/impressum")
    copyright_page = client.get("/copyright")

    assert impressum.status_code == 200
    assert copyright_page.status_code == 200
