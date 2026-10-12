from pydantic import ValidationError
import pytest

from schemas.generate import GenerateRequest


def make_request(fields):
    return GenerateRequest(
        table_name="test_data",
        fields=fields,
        count=5,
        format="json",
    )


def test_valid_request():
    request = make_request([
        {
            "type": "firstname",
            "name": "first_name",
        },
        {
            "type": "city",
            "name": "city_name",
        },
    ])

    assert len(request.fields) == 2


def test_invalid_field_type():
    with pytest.raises(ValidationError):
        make_request([
            {
                "type": "unknown_field",
                "name": "unknown",
            }
        ])


def test_invalid_column_name():
    with pytest.raises(ValidationError):
        make_request([
            {
                "type": "firstname",
                "name": "first-name",
            }
        ])


def test_duplicate_column_names():
    with pytest.raises(ValidationError):
        make_request([
            {
                "type": "firstname",
                "name": "person",
            },
            {
                "type": "lastname",
                "name": "PERSON",
            },
        ])


def test_reserved_id_name():
    with pytest.raises(ValidationError):
        make_request([
            {
                "type": "firstname",
                "name": "id",
            }
        ])


def test_invalid_count():
    with pytest.raises(ValidationError):
        GenerateRequest(
            table_name="users",
            fields=[
                {
                    "type": "firstname",
                    "name": "name",
                }
            ],
            count=10001,
        )
