"""Traduz erros de domínio e de aplicação para Problem Details (RFC 9457)."""

from collections.abc import Awaitable, Callable
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.application.shared import ApplicationError, ConcurrencyConflictError, NotFoundError
from app.domain.seedwork import BusinessRuleViolation, DomainError, InvariantViolation

_STATUS_BY_ERROR: tuple[tuple[type[DomainError | ApplicationError], HTTPStatus], ...] = (
    (InvariantViolation, HTTPStatus.UNPROCESSABLE_ENTITY),
    (BusinessRuleViolation, HTTPStatus.CONFLICT),
    (NotFoundError, HTTPStatus.NOT_FOUND),
    (ConcurrencyConflictError, HTTPStatus.CONFLICT),
)


def register_error_handlers(app: FastAPI) -> None:
    for error_type, status in _STATUS_BY_ERROR:
        app.add_exception_handler(error_type, _problem_handler(status))


def _problem_handler(status: HTTPStatus) -> Callable[[Request, Exception], Awaitable[JSONResponse]]:
    async def handle(request: Request, error: Exception) -> JSONResponse:
        assert isinstance(error, DomainError | ApplicationError)
        return JSONResponse(
            status_code=status,
            media_type="application/problem+json",
            content={
                "type": "about:blank",
                "title": status.phrase,
                "status": status.value,
                "detail": error.message,
                "code": error.code,
                "instance": request.url.path,
            },
        )

    return handle
