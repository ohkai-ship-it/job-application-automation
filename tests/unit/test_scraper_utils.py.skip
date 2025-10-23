import pytest

from src.scraper import clean_job_title, split_address


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Data Scientist (m/w/d)", "Data Scientist"),
        ("Senior Engineer (m/f/d) -", "Senior Engineer"),
        ("Product Manager (gn)", "Product Manager"),
        ("Entwickler m/w/d", "Entwickler"),
        ("Lead Dev (all genders)", "Lead Dev"),
        ("Software Engineer (X/W/M)", "Software Engineer"),
        ("No markers here", "No markers here"),
        (None, None),
        ("  - Junior Developer  ", "Junior Developer"),
    ],
)
def test_clean_job_title(raw, expected):
    assert clean_job_title(raw) == expected


def test_split_address_basic():
    address = {"streetAddress": "Main St 1", "postalCode": "10115", "addressLocality": "Berlin"}
    line1, line2 = split_address(address)
    assert line1 == "Main St 1"
    assert line2 == "10115 Berlin"


def test_split_address_missing_parts():
    # Missing postal code
    address = {"streetAddress": "Main St 1", "addressLocality": "Berlin"}
    line1, line2 = split_address(address)
    assert line1 == "Main St 1"
    assert line2 == "Berlin"

    # Missing city
    address = {"streetAddress": "Main St 1", "postalCode": "10115"}
    line1, line2 = split_address(address)
    assert line1 == "Main St 1"
    assert line2 == "10115"

    # Missing street
    address = {"postalCode": "10115", "addressLocality": "Berlin"}
    line1, line2 = split_address(address)
    assert line1 == ""
    assert line2 == "10115 Berlin"


def test_split_address_empty():
    line1, line2 = split_address({})
    assert line1 == ""
    assert line2 == ""
