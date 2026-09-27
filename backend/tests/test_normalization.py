import pytest
from app.services.normalization_service import NormalizationService

def test_email_normalization():
    assert NormalizationService.normalize_email(" JOHN@GMAIL.COM ") == "john@gmail.com"
    assert NormalizationService.normalize_email("sarah.c@cyberdyne.com") == "sarah.c@cyberdyne.com"
    assert NormalizationService.normalize_email(" N/A ") is None
    assert NormalizationService.normalize_email("") is None
    assert NormalizationService.normalize_email("   ") is None

def test_text_and_name_normalization():
    assert NormalizationService.normalize_name("  John    Doe ") == "John Doe"
    assert NormalizationService.normalize_name("JOHN DOE") == "John Doe"
    assert NormalizationService.normalize_name("john doe") == "John Doe"
    assert NormalizationService.normalize_name("Sarah Connor") == "Sarah Connor"
    assert NormalizationService.normalize_name("N/A") is None

def test_phone_normalization():
    assert NormalizationService.normalize_phone("+91 98765-43210") == "9876543210"
    assert NormalizationService.normalize_phone("9876543210") == "9876543210"
    assert NormalizationService.normalize_phone("+1-555-0199") == "15550199"
    assert NormalizationService.normalize_phone("(555) 0199") == "5550199"
    assert NormalizationService.normalize_phone("N/A") is None
    assert NormalizationService.normalize_phone("") is None


def test_null_sentinel_normalization():
    for null_val in ["NULL", "null", "N/A", "n/a", "", " ", "  ", "-", "None", "none", "nan"]:
        assert NormalizationService.normalize_null(null_val) is None

def test_raw_record_dict_normalization():
    raw_record = {
        "customer_id": "C-8812",
        "name": "John Doe ",
        "email_id": " JOHN@GMAIL.COM ",
        "contact_no": "+91 98765-43210",
        "address": "124 Marine Drive, Mumbai"
    }

    mappings = {
        "customer_id": "member_id",
        "name": "name",
        "email_id": "email",
        "contact_no": "phone",
        "address": "address"
    }

    normalized = NormalizationService.normalize_record_dict(raw_record, mappings)

    assert normalized["email"] == "john@gmail.com"
    assert normalized["phone"] == "9876543210"
    assert normalized["name"] == "John Doe"
    assert normalized["member_id"] == "c-8812"
    assert normalized["address"] == "124 Marine Drive, Mumbai"
