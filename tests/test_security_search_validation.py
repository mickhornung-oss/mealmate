from __future__ import annotations


def test_search_rejects_extremely_long_title_query(client):
    very_long_query = "A" * 10000
    response = client.get("/", params={"title": very_long_query})
    assert response.status_code in {400, 422}


def test_search_validates_page_and_per_page_bounds(client):
    page_zero = client.get("/", params={"page": 0})
    page_negative = client.get("/", params={"page": -5})
    per_page_too_large = client.get("/", params={"per_page": 1000000})

    assert page_zero.status_code in {400, 422}
    assert page_negative.status_code in {400, 422}
    assert per_page_too_large.status_code in {400, 422}


def test_search_rejects_invalid_sort_key_injection(client):
    injected = client.get("/", params={"sort": "__something__"})
    sql_like = client.get("/", params={"sort": "date;DROP TABLE recipes;--"})

    assert injected.status_code in {400, 422}
    assert sql_like.status_code in {400, 422}


def test_search_handles_unicode_and_special_chars_without_500(client):
    samples = [
        "ÄÖÜß Kuchen",
        "👩🏽‍🍳🍲",
        "Cafe\u0301",
        "Komm zurück!",
        "' OR 1=1 --",
    ]
    for sample in samples:
        response = client.get("/", params={"title": sample, "ingredient": sample})
        assert response.status_code < 500
