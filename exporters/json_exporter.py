from typing import Any

from schemas.generate import GenerateResponse


def export_json(
    rows: list[dict[str, Any]],
    ddl: str | None = None,
) -> dict:
    response = GenerateResponse(
        data=rows,
        ddl=ddl,
        format="json",
    )

    return response.model_dump()
