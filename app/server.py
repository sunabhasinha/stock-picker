"""
The M2 auth server (spec: docs/specs/auth-layer.md; ADR-0006).

FastAPI application factory. Run locally:

    uvicorn app.server:app --port 8000

Interactive API docs (generated from the code, never hand-written):
http://127.0.0.1:8000/docs (Swagger UI) and /redoc.

Security posture, enforced here:
- identity comes ONLY from the session cookie -> hashed lookup ->
  sessions row (service.user_for_session); never from client fields
- one uniform 401 body for every authentication failure
- session cookie: httpOnly + SameSite=Lax (+ Secure when
  APP_COOKIE_SECURE=1 - REQUIRED in any deployment; default off only
  because local dev runs plain http)
- state-changing requests with an Origin header must match APP_BASE_URL
  (second CSRF line behind SameSite)
- no password, token, or cookie value is ever logged or echoed
- user-data access runs inside rls_transaction (app_rls + app.user_id)
"""

from __future__ import annotations

import datetime as dt
import os
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from app.auth.emailer import ConsoleEmailTransport, EmailTransport
from app.auth.service import (
    GENERIC_AUTH_FAILURE,
    GENERIC_FLOW_RESPONSE,
    SESSION_TTL,
    AuthError,
    AuthService,
)
from app.db.repository import Repository
from app.db.session import make_session_factory, rls_transaction
from sunabha_agent.portfolio.category_engine import PRESET_CATEGORIES

SESSION_COOKIE = "sp_session"
STATIC_DIR = Path(__file__).resolve().parent / "static"


# --- request/response bodies (also feed the generated OpenAPI docs) -------

class Credentials(BaseModel):
    email: str = Field(max_length=320)
    password: str = Field(max_length=1024)


class EmailOnly(BaseModel):
    email: str = Field(max_length=320)


class ResetConfirm(BaseModel):
    token: str = Field(max_length=128)
    new_password: str = Field(max_length=1024)


class PasswordChange(BaseModel):
    current_password: str = Field(max_length=1024)
    new_password: str = Field(max_length=1024)


class PortfolioCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category_key: str = Field(max_length=40)


def create_app(
    session_factory=None,
    emailer: EmailTransport | None = None,
    base_url: str | None = None,
) -> FastAPI:
    """Factory - tests inject a SQLite session factory and a capturing
    email transport; production uses env-configured defaults."""
    base_url = (base_url or os.environ.get("APP_BASE_URL",
                                           "http://127.0.0.1:8000")).rstrip("/")
    cookie_secure = os.environ.get("APP_COOKIE_SECURE", "") == "1"
    emailer = emailer or ConsoleEmailTransport()
    _factory = session_factory  # created lazily so import needs no DATABASE_URL

    app = FastAPI(title="Sunabha Agent — product API", version="0.2.0")

    def factory():
        nonlocal _factory
        if _factory is None:
            _factory = make_session_factory()
        return _factory

    # --- plumbing -----------------------------------------------------------

    def db_session():
        session = factory()()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def auth_service(db=Depends(db_session)) -> AuthService:
        return AuthService(db, emailer, base_url=base_url)

    def current_user(request: Request, service=Depends(auth_service)):
        token = request.cookies.get(SESSION_COOKIE)
        if not token:
            raise HTTPException(401, GENERIC_AUTH_FAILURE)
        try:
            return service.user_for_session(token)
        except AuthError:
            raise HTTPException(401, GENERIC_AUTH_FAILURE)

    @app.exception_handler(AuthError)
    async def _auth_error(request: Request, exc: AuthError):
        return JSONResponse({"detail": GENERIC_AUTH_FAILURE}, status_code=401)

    @app.exception_handler(ValueError)
    async def _value_error(request: Request, exc: ValueError):
        return JSONResponse({"detail": str(exc)}, status_code=400)

    @app.middleware("http")
    async def origin_check(request: Request, call_next):
        # Second CSRF line behind SameSite=Lax: browsers attach Origin to
        # unsafe cross-site requests; if present, it must be our own.
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            origin = request.headers.get("origin")
            if origin and urlsplit(origin).netloc != urlsplit(base_url).netloc:
                return JSONResponse({"detail": "origin not allowed"},
                                    status_code=403)
        return await call_next(request)

    def set_session_cookie(response: Response, token: str) -> None:
        response.set_cookie(
            SESSION_COOKIE, token,
            max_age=int(SESSION_TTL.total_seconds()),
            httponly=True, samesite="lax", secure=cookie_secure, path="/",
        )

    # --- auth routes --------------------------------------------------------

    @app.post("/auth/register", status_code=202)
    def register(body: Credentials, service=Depends(auth_service)):
        service.register(body.email, body.password)
        return {"detail": GENERIC_FLOW_RESPONSE}

    @app.get("/auth/verify")
    def verify(token: str, service=Depends(auth_service)):
        service.verify_email(token)
        return {"detail": "email verified — you can log in now"}

    @app.post("/auth/login", status_code=204)
    def login(body: Credentials, request: Request, response: Response,
              service=Depends(auth_service)):
        ip = request.client.host if request.client else "unknown"
        token = service.login(body.email, body.password, ip=ip)
        set_session_cookie(response, token)

    @app.post("/auth/logout", status_code=204)
    def logout(request: Request, response: Response,
               service=Depends(auth_service)):
        token = request.cookies.get(SESSION_COOKIE)
        if token:
            service.logout(token)
        response.delete_cookie(SESSION_COOKIE, path="/")

    @app.post("/auth/password-reset/request", status_code=202)
    def reset_request(body: EmailOnly, service=Depends(auth_service)):
        service.request_password_reset(body.email)
        return {"detail": GENERIC_FLOW_RESPONSE}

    @app.post("/auth/password-reset/confirm", status_code=204)
    def reset_confirm(body: ResetConfirm, service=Depends(auth_service)):
        service.confirm_password_reset(body.token, body.new_password)

    # --- authenticated API ----------------------------------------------------

    @app.get("/api/me")
    def me(user=Depends(current_user)):
        return {"id": str(user.id), "email": user.email}

    @app.post("/api/password", status_code=204)
    def change_password(body: PasswordChange, user=Depends(current_user),
                        service=Depends(auth_service)):
        service.change_password(user, body.current_password, body.new_password)

    @app.get("/api/portfolios")
    def list_portfolios(user=Depends(current_user)):
        with rls_transaction(factory(), user.id) as session:
            return [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "category_key": p.category_key,
                    "commitment_started_on": p.commitment_started_on.isoformat(),
                }
                for p in Repository(session).portfolios_for_user(user.id)
            ]

    @app.post("/api/portfolios", status_code=201)
    def create_portfolio(body: PortfolioCreate, user=Depends(current_user)):
        if body.category_key not in PRESET_CATEGORIES:
            raise HTTPException(
                400, f"category_key must be one of {sorted(PRESET_CATEGORIES)}"
            )
        with rls_transaction(factory(), user.id) as session:
            portfolio = Repository(session).create_portfolio(
                user.id, body.name, body.category_key, dt.date.today()
            )
            return {"id": str(portfolio.id), "name": portfolio.name,
                    "category_key": portfolio.category_key}

    # --- minimal pages ---------------------------------------------------------

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def index():
        return (STATIC_DIR / "auth.html").read_text()

    return app


app = create_app()
