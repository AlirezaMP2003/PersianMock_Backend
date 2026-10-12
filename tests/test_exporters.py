import pytest

from exporters.common import (
    get_columns,
    quote_identifier,
    sql_literal,
    spreadsheet_safe,
)
from exporters.sql_exporter import build_create_table_sql
from schemas.generate import FieldItem


def test_quote_identifier():
    assert quote_identifier("order") == '"order"'


def test_sql_literal():
    assert sql_literal(None) == "NULL"
    assert sql_literal(True) == "TRUE"
    assert sql_literal(1402) == "1402"
    assert sql_literal("O'Brien") == "'O''Brien'"


@pytest.mark.parametrize(
    "value",
    ["=1+1", "+SUM(A1:A2)", "-1+2", "@SUM(A1:A2)"],
)
def test_spreadsheet_safe(value):
    assert spreadsheet_safe(value) == "'" + value


def test_spreadsheet_normal_text():
    assert spreadsheet_safe("تهران") == "تهران"
    assert spreadsheet_safe("09123456789") == "09123456789"


def test_get_columns():
    fields = [
        FieldItem(type="id", name="id"),
        FieldItem(type="city", name="city_name"),
    ]

    assert get_columns(fields) == [
        "id",
        "city_name",
    ]


def test_create_table_sql():
    fields = [
        FieldItem(
            type="car_name",
            name="model",
        ),
        FieldItem(
            type="car_year",
            name="model_year",
        ),
    ]

    sql = build_create_table_sql(
        "vehicles",
        fields,
    )

    assert '"id" INTEGER PRIMARY KEY' in sql
    assert '"model" VARCHAR(100)' in sql
    assert '"model_year" INTEGER' in sql
    assert sql.startswith(
        'CREATE TABLE IF NOT EXISTS "vehicles"'
    )
