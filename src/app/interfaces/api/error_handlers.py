"""Traduz erros de domínio e de aplicação para Problem Details (RFC 9457)."""

from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.application.shared import ApplicationError, ConcurrencyConflictError, NotFoundError
from app.domain.seedwork import BusinessRuleViolation, DomainError, InvariantViolation

# Títulos fixos (RFC 9110): não dependem da versão do Python.
_PROBLEM_BY_ERROR: tuple[tuple[type[DomainError | ApplicationError], int, str], ...] = (
    (InvariantViolation, 422, "Unprocessable Content"),
    (BusinessRuleViolation, 409, "Conflict"),
    (NotFoundError, 404, "Not Found"),
    (ConcurrencyConflictError, 409, "Conflict"),
)


def register_error_handlers(app: FastAPI) -> None:
    for error_type, status, title in _PROBLEM_BY_ERROR:
        app.add_exception_handler(error_type, _problem_handler(status, title))


def _problem_handler(
    status: int, title: str
) -> Callable[[Request, Exception], Awaitable[JSONResponse]]:
    async def handle(request: Request, error: Exception) -> JSONResponse:
        assert isinstance(error, DomainError | ApplicationError)
        return JSONResponse(
            status_code=status,
            media_type="application/problem+json",
            content={
                "type": "about:blank",
                "title": title,
                "status": status,
                "detail": error.message,
                "code": error.code,
                "instance": request.url.path,
            },
        )

    return handle
