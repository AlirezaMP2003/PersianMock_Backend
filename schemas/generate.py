import re
from typing import Any, Dict, List, Literal, Optional

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)

IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

ALLOWED_FIELD_TYPES = frozenset({
    "id",
    "firstname",
    "lastname",
    "email",
    "username",
    "password",
    "gender",
    "province",
    "city",
    "car_company",
    "car_name",
    "car_color",
    "car_year",
    "mobile_number",
    "postal_code",
})


class FieldItem(BaseModel):
    type: str
    name: str

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        if value not in ALLOWED_FIELD_TYPES:
            raise ValueError(
                f"Unsupported field type: {value!r}"
            )
        return value

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if (
            len(value) > 63
            or not IDENTIFIER_RE.fullmatch(value)
        ):
            raise ValueError(
                "Column name must be 1-63 ASCII characters: "
                "letters, digits, underscores; "
                "cannot start with a digit"
            )
        return value


class GenerateRequest(BaseModel):
    table_name: str = Field(
        ...,
        min_length=1,
        max_length=63,
        pattern=r"^[A-Za-z_][A-Za-z0-9_]*$",
    )
    fields: List[FieldItem] = Field(..., min_length=1)
    count: int = Field(default=5, ge=1, le=10000)
    include_create_table: bool = False
    format: Literal[
        "json", "csv", "sql", "excel"
    ] = "sql"

    @model_validator(mode="after")
    def validate_field_names(self):
        names = [
            field.name.lower()
            for field in self.fields
        ]

        if len(names) != len(set(names)):
            raise ValueError(
                "Column names must be unique "
                "(case-insensitive)"
            )

        for field in self.fields:
            if (
                field.type == "id"
                and field.name.lower() != "id"
            ):
                raise ValueError(
                    "The id field must be named 'id'"
                )

            if (
                field.type != "id"
                and field.name.lower() == "id"
            ):
                raise ValueError(
                    "The column 'id' is reserved "
                    "for automatic IDs"
                )

        return self


class GenerateResponse(BaseModel):
    data: List[Dict[str, Any]]
    ddl: Optional[str] = None
    format: Literal["json", "csv", "sql", "excel"]
