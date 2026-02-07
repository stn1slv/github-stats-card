"""Tests for utility functions."""

from src.core.utils import k_formatter, clamp_value, encode_html, parse_list_arg


def test_k_formatter_less_than_thousand():
    assert k_formatter(500) == "500"
    assert k_formatter(999) == "999"


def test_k_formatter_thousands():
    assert k_formatter(1000) == "1k"
    assert k_formatter(1500) == "1.5k"
    assert k_formatter(6626) == "6.6k"
    assert k_formatter(10000) == "10k"


def test_k_formatter_with_precision():
    assert k_formatter(6626, precision=0) == "7k"
    assert k_formatter(6626, precision=1) == "6.6k"
    assert k_formatter(6626, precision=2) == "6.63k"


def test_k_formatter_negative():
    assert k_formatter(-1500) == "-1.5k"


def test_clamp_value():
    assert clamp_value(5, 0, 10) == 5
    assert clamp_value(-5, 0, 10) == 0
    assert clamp_value(15, 0, 10) == 10
    assert clamp_value(7.5, 0, 10) == 7.5


def test_encode_html():
    assert encode_html("Hello World") == "Hello World"
    assert encode_html("<script>") == "&lt;script&gt;"
    assert encode_html("A & B") == "A &amp; B"
    assert encode_html('"quoted"') == "&quot;quoted&quot;"
    assert encode_html("'single'") == "&#39;single&#39;"


def test_parse_list_arg():
    assert parse_list_arg(None) == []
    assert parse_list_arg("") == []
    assert parse_list_arg("foo") == ["foo"]
    assert parse_list_arg("foo,bar") == ["foo", "bar"]
    assert parse_list_arg(" foo , bar ") == ["foo", "bar"]
    assert parse_list_arg(["foo", "bar"]) == ["foo", "bar"]
    assert parse_list_arg([" foo ", " bar "]) == ["foo", "bar"]