from fastapi import APIRouter, Depends, Request

from app.dependencies import get_current_user_optional, template_context
from app.models import User
from app.views import templates

router = APIRouter(tags=["legal"])


@router.get("/impressum")
def impressum_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
):
    return templates.TemplateResponse(
        "impressum.html",
        template_context(request, current_user, title="Impressum"),
    )


@router.get("/copyright")
def copyright_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
):
    return templates.TemplateResponse(
        "copyright.html",
        template_context(request, current_user, title="Copyright"),
    )
