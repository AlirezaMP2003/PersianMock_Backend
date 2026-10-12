import csv
import io
from typing import Any

from fastapi.responses import StreamingResponse

from exporters.common import spreadsheet_safe


def export_csv(
    rows: list[dict[str, Any]],
    columns: list[str],
    table_name: str,
) -> StreamingResponse:

    output = io.StringIO(newline="")
    writer = csv.writer(output)

    writer.writerow(columns)

    for row in rows:
        writer.writerow([
            spreadsheet_safe(row[column])
            for column in columns
        ])

    csv_bytes = output.getvalue().encode("utf-8-sig")

    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition":
            f'attachment; filename="{table_name}.csv"'
        },
    )
