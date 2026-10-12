from typing import Any

from fastapi import Response

from exporters.common import (
    SQL_TYPES,
    get_columns,
    quote_identifier,
    sql_literal,
)


def build_create_table_sql(
    table_name: str,
    fields,
) -> str:
    columns = ['"id" INTEGER PRIMARY KEY']

    for field in fields:
        if field.type == "id":
            continue

        column_name = quote_identifier(field.name)
        sql_type = SQL_TYPES[field.type]

        columns.append(
            f"{column_name} {sql_type}"
        )

    columns_sql = ", ".join(columns)

    return (
        f"CREATE TABLE IF NOT EXISTS "
        f"{quote_identifier(table_name)} "
        f"({columns_sql});"
    )


def export_sql(
    rows: list[dict[str, Any]],
    table_name: str,
    fields,
    ddl: str | None = None,
) -> Response:

    columns = get_columns(fields)

    columns_sql = ", ".join(
        quote_identifier(column)
        for column in columns
    )

    sql_rows = []

    for row in rows:
        values_sql = ", ".join(
            sql_literal(row[column])
            for column in columns
        )

        sql_rows.append(
            f"({values_sql})"
        )

    insert_sql = (
        f"INSERT INTO "
        f"{quote_identifier(table_name)} "
        f"({columns_sql}) VALUES\n"
        + ",\n".join(sql_rows)
        + ";"
    )

    sql_text = "\n\n".join(
        part
        for part in [ddl, insert_sql]
        if part
    )

    return Response(
        content=sql_text,
        media_type="text/plain; charset=utf-8",
    )
