import asyncio
import os
import re
import sys
import time
import uuid
from pathlib import Path

import httpx

sys.path.append(str(Path(__file__).resolve().parents[1]))


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def csrf_token_from_cookies(client: httpx.AsyncClient) -> str:
    token = client.cookies.get("csrf_token")
    ensure(bool(token), "Missing csrf_token cookie.")
    return str(token)


async def build_client() -> httpx.AsyncClient:
    base_url = os.getenv("SMOKE_BASE_URL", "").strip()
    if base_url:
        return httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            follow_redirects=False,
            timeout=30.0,
        )
    from app.main import app

    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
        follow_redirects=False,
        timeout=30.0,
    )


def parse_recipe_id(location: str) -> int:
    match = re.search(r"/recipes/(\d+)", location or "")
    ensure(match is not None, f"Could not parse recipe id from location '{location}'.")
    return int(match.group(1))


async def run() -> None:
    client = await build_client()
    async with client:
        health = await client.get("/healthz")
        ensure(health.status_code == 200, f"/healthz failed with {health.status_code}.")
        ensure(health.json().get("status") == "ok", "/healthz did not return status=ok.")
        print("[ok] healthz")

        unique = f"{int(time.time())}_{uuid.uuid4().hex[:8]}"
        email = f"smoke_{unique}@example.local"
        password = "SmokePass123!"

        register_page = await client.get("/register")
        ensure(register_page.status_code == 200, f"/register GET failed with {register_page.status_code}.")
        csrf = csrf_token_from_cookies(client)

        register = await client.post(
            "/register",
            data={"email": email, "password": password, "csrf_token": csrf},
            headers={"X-CSRF-Token": csrf},
        )
        ensure(register.status_code in {302, 303}, f"/register failed with {register.status_code}.")
        ensure(bool(client.cookies.get("access_token")), "Register did not set access_token cookie.")
        print("[ok] register + auth cookie")

        logout = await client.post(
            "/logout",
            data={"csrf_token": csrf},
            headers={"X-CSRF-Token": csrf},
        )
        ensure(logout.status_code in {302, 303}, f"/logout failed with {logout.status_code}.")

        login_page = await client.get("/login")
        ensure(login_page.status_code == 200, f"/login GET failed with {login_page.status_code}.")
        csrf = csrf_token_from_cookies(client)

        login = await client.post(
            "/login",
            data={"email": email, "password": password, "csrf_token": csrf},
            headers={"X-CSRF-Token": csrf},
        )
        ensure(login.status_code in {302, 303}, f"/login failed with {login.status_code}.")
        ensure(bool(client.cookies.get("access_token")), "Login did not set access_token cookie.")
        print("[ok] login + auth cookie")

        new_recipe_page = await client.get("/recipes/new")
        ensure(new_recipe_page.status_code == 200, f"/recipes/new GET failed with {new_recipe_page.status_code}.")
        csrf = csrf_token_from_cookies(client)

        create_recipe = await client.post(
            "/recipes/new",
            data={
                "title": f"Smoke Recipe {unique}",
                "description": "Created by smoke test.",
                "instructions": "Step 1\nStep 2",
                "category": "Smoke",
                "title_image_url": "",
                "prep_time_minutes": "12",
                "difficulty": "easy",
                "ingredients_text": "egg|1|60",
                "csrf_token": csrf,
            },
            headers={"X-CSRF-Token": csrf},
        )
        ensure(create_recipe.status_code in {302, 303}, f"Recipe create failed with {create_recipe.status_code}.")
        recipe_id = parse_recipe_id(create_recipe.headers.get("location", ""))
        print(f"[ok] create recipe id={recipe_id}")

        pdf = await client.get(f"/recipes/{recipe_id}/pdf")
        ensure(pdf.status_code == 200, f"PDF endpoint failed with {pdf.status_code}.")
        content_type = pdf.headers.get("content-type", "")
        ensure(content_type.startswith("application/pdf"), f"Unexpected PDF content type '{content_type}'.")
        ensure(len(pdf.content) > 100, "PDF response looks too small.")
        print("[ok] pdf endpoint")

    print("Smoke test passed.")


if __name__ == "__main__":
    asyncio.run(run())
