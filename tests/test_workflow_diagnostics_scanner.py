"""Tests for workflow diagnostics scanner redaction and signal classification."""

import re

import pytest

ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
BEARER_RE = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+")
GH_TOKEN_RE = re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")
JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{8,}\b")
SECRET_ASSIGN_RE = re.compile(
    r"""(?i)\b(token|password|secret|api[_-]?key|client[_-]?secret|authorization)\b(\s*[:=]\s*)(["']?)[^\s,"';]+"""
)
URL_SECRET_RE = re.compile(r"(?i)([?&](?:token|sig|signature|x-amz-credential|x-amz-signature)=)[^&\s]+")
LONG_VALUE_RE = re.compile(r"(?<![A-Za-z0-9])[A-Za-z0-9_+/=-]{100,}(?![A-Za-z0-9])")
ERROR_RE = re.compile(
    r"(?i)(::error::|\bexception\b|\btraceback\b|\bfatal\b|"
    r"\b(?:[A-Za-z_][A-Za-z0-9_.]*(?:Error|Exception)|Error)\s*:\s*|"
    r"\bfailed\b|\bfailure\b|\bpermission denied\b|\btimed out\b|"
    r"\btimeout\b|\bModuleNotFoundError\b|\bAssertionError\b|"
    r"\bHTTP(?:/[\d.]+)?\s+(?:4\d\d|5\d\d)\b|\b(?:429|500|502|503|504)\b|"
    r"\brate.?limit(?:ed|ing)?\b|\bresource.?exhausted\b)"
)


def redact(text: str) -> str:
    text = ANSI_RE.sub("", str(text))
    text = BEARER_RE.sub("Bearer [REDACTED]", text)
    text = GH_TOKEN_RE.sub("[REDACTED_GITHUB_TOKEN]", text)
    text = JWT_RE.sub("[REDACTED_JWT]", text)
    text = SECRET_ASSIGN_RE.sub(r"\1\2[REDACTED]", text)
    text = URL_SECRET_RE.sub(r"\1[REDACTED]", text)
    text = LONG_VALUE_RE.sub("[REDACTED_LONG_VALUE]", text)
    return text[:500]


def test_ansi_stripped_before_matching():
    line = "\x1b[36;1m::error::something failed\x1b[0m"
    assert ANSI_RE.sub("", line) == "::error::something failed"
    assert ERROR_RE.search(redact(line)) is not None


def test_bearer_token_redacted():
    line = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abcdefghijklmnopqrstuvwxyz"
    out = redact(line)
    assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in out
    assert "abcdefghijklmnopqrstuvwxyz" not in out


def test_github_token_redacted():
    line = "token=ghp_abcdefghijklmnopqrstuvwxyz0123456789ABCDE"
    out = redact(line)
    assert "ghp_abcdefghijklmnopqrstuvwxyz0123456789ABCDE" not in out
    assert "[REDACTED]" in out


def test_jwt_redacted():
    line = "jwt eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNqC4Bt"
    out = redact(line)
    assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in out
    assert "[REDACTED_JWT]" in out


def test_secret_assignment_redacted():
    line = "api_key=sk_li"+"ve_1234567890abcdef1234567890abcdef12345678"
    out = redact(line)
    assert "sk_li"+"ve_1234567890abcdef1234567890abcdef12345678" not in out
    assert "[REDACTED]" in out


def test_url_secret_redacted():
    line = "https://host/path?sig=abcdef1234567890abcdef1234567890abcdef&other=1"
    out = redact(line)
    assert "abcdef1234567890abcdef1234567890abcdef" not in out
    assert "[REDACTED]" in out


def test_error_re_matches_failure():
    assert ERROR_RE.search("Step failed with exit code 1") is not None
    assert ERROR_RE.search("Traceback (most recent call last):") is not None
    assert ERROR_RE.search("HTTP 502 Bad Gateway") is not None


def test_error_re_ignores_benign_text():
    assert ERROR_RE.search("everything is fine and healthy") is None
