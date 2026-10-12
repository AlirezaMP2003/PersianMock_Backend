import io
from typing import Any

from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from exporters.common import spreadsheet_safe


def export_excel(
    rows: list[dict[str, Any]],
    columns: list[str],
    table_name: str,
) -> StreamingResponse:

    try:
        import pandas as pd
        import openpyxl

    except ImportError as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Excel export requires "
                "pandas and openpyxl."
            ),
        ) from exc

    safe_rows = [
        {
            column: spreadsheet_safe(row[column])
            for column in columns
        }
        for row in rows
    ]

    dataframe = pd.DataFrame(
        safe_rows,
        columns=columns,
    )

    output = io.BytesIO()

    dataframe.to_excel(
        output,
        index=False,
        engine="openpyxl",
    )

    output.seek(0)

    return StreamingResponse(
        output,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
            f'attachment; filename="{table_name}.xlsx"'
        },
    )
