from __future__ import annotations

import html

from sqlalchemy import and_, select

from app.models import RecipeSubmission, Review
from tests.helpers import create_admin_user, create_normal_user, create_published_recipe, post_form, unique_email


def _login(client, identifier: str, password: str) -> None:
    response = post_form(
        client,
        "/login",
        data={"identifier": identifier, "password": password},
        referer_page="/login",
        follow_redirects=False,
    )
    assert response.status_code in {302, 303}


def test_submission_whitespace_rejected_and_long_payload_bounded(client, db_session_factory):
    whitespace_response = post_form(
        client,
        "/submit",
        data={
            "title": "   ",
            "description": "Beschreibung",
            "instructions": "   ",
            "category_select": "Unkategorisiert",
            "difficulty": "medium",
        },
        referer_page="/submit",
    )
    assert whitespace_response.status_code == 400

    user_email = unique_email("content-abuse")
    password = "UserPass123!"
    with db_session_factory() as db:
        user = create_normal_user(db, user_email, password)
        user_id = int(user.id)

    _login(client, user_email, password)

    very_long_title = "T" * 5000
    very_long_description = "Beschreibung " + ("x" * 12000)
    very_long_instructions = "Schritt eins\n" + ("A" * 20000)

    long_response = post_form(
        client,
        "/submit",
        data={
            "title": very_long_title,
            "description": very_long_description,
            "instructions": very_long_instructions,
            "category_select": "Dessert",
            "difficulty": "easy",
        },
        referer_page="/submit",
        follow_redirects=False,
    )
    assert long_response.status_code in {302, 303}

    with db_session_factory() as db:
        submission = db.scalar(
            select(RecipeSubmission)
            .where(RecipeSubmission.submitter_user_id == user_id)
            .order_by(RecipeSubmission.id.desc())
        )
        assert submission is not None
        assert len(submission.title) <= 255
        assert submission.title == very_long_title[:255]
        assert submission.description.startswith("Beschreibung")
        assert submission.instructions.startswith("Schritt eins")


def test_review_comment_xss_is_escaped_and_whitespace_normalized(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("abuse-admin"), "AdminPass123!")
        user = create_normal_user(db, unique_email("abuse-user"), "UserPass123!")
        recipe = create_published_recipe(db, admin.id, title="Abuse Review Recipe")
        recipe_id = int(recipe.id)
        user_email = user.email
        user_id = int(user.id)

    _login(client, user_email, "UserPass123!")

    whitespace_review = post_form(
        client,
        f"/recipes/{recipe_id}/reviews",
        data={"rating": "4", "comment": "    "},
        referer_page=f"/recipes/{recipe_id}",
        follow_redirects=False,
    )
    assert whitespace_review.status_code in {302, 303}

    with db_session_factory() as db:
        stored = db.scalar(
            select(Review).where(
                and_(
                    Review.recipe_id == recipe_id,
                    Review.user_id == user_id,
                )
            )
        )
        assert stored is not None
        assert stored.comment == ""

    payload_script = "<script>alert(1)</script>"
    payload_img = "<img src=x onerror=alert(1)>"
    xss_review = post_form(
        client,
        f"/recipes/{recipe_id}/reviews",
        data={"rating": "5", "comment": f"{payload_script} {payload_img}"},
        referer_page=f"/recipes/{recipe_id}",
        follow_redirects=False,
    )
    assert xss_review.status_code in {302, 303}

    detail = client.get(f"/recipes/{recipe_id}")
    assert detail.status_code == 200
    body = detail.text
    assert payload_script not in body
    assert payload_img not in body
    assert html.escape(payload_script) in body
    assert html.escape(payload_img) in body


def test_username_validation_blocks_abusive_patterns(client, db_session_factory):
    email = unique_email("abuse-username")
    password = "UserPass123!"

    with db_session_factory() as db:
        create_normal_user(db, email, password)

    _login(client, email, password)

    abusive_usernames = [
        "   ",
        "a" * 31,
        "<b>root</b>",
        "name%_sql",
    ]

    for value in abusive_usernames:
        response = post_form(
            client,
            "/profile/username",
            data={"username": value},
            referer_page="/me",
        )
        assert response.status_code in {400, 409}

    unicode_edge_value = "jo\u0308rg\u200f"
    unicode_response = post_form(
        client,
        "/profile/username",
        data={"username": unicode_edge_value},
        referer_page="/me",
    )
    assert unicode_response.status_code in {400, 409}
    assert unicode_response.status_code < 500


def test_unicode_and_wildcard_inputs_do_not_trigger_500(client):
    samples = [
        "Cafe\u0301",
        "\u200fRTL",
        "\u202Eabc",
        "ÄÖÜß",
        "👩🏽\u200d🍳",
        "%",
        "_",
        "100%_mix",
    ]
    for sample in samples:
        response = client.get("/", params={"title": sample, "ingredient": sample})
        assert response.status_code < 500
