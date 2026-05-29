"""Tests for _slugify_romanji — ensures output is purely ASCII romaji slugs."""

from KeiNews.main import _slugify_romanji


def test_japanese_katakana_becomes_ascii():
    """Katakana titles are converted to ASCII romaji."""
    assert _slugify_romanji("テスト") == "tesuto"
    assert _slugify_romanji("ニュース") == "nyuusu"
    assert _slugify_romanji("ジャパン") == "japan"


def test_japanese_hiragana_becomes_ascii():
    """Hiragana titles are converted to ASCII romaji."""
    assert _slugify_romanji("てすと") == "tesuto"


def test_japanese_kANJI_becomes_ascii():
    """Kanji characters are stripped to nothing."""
    assert _slugify_romanji("新聞") == ""


def test_mixed_japanese_becomes_ascii():
    """Mixed kanji/katakana/hiragana titles produce ASCII-only slugs."""
    assert _slugify_romanji("東京ニュース") == "nyuusu"
    assert _slugify_romanji("気-news") == "news"


def test_completely_japanese_produces_empty():
    """A title with only kanji produces an empty string."""
    assert _slugify_romanji("日本語") == ""


def test_ascii_only_stays_ascii():
    """Pure ASCII titles pass through unchanged (minus non-alphanumeric cleanup)."""
    assert _slugify_romanji("Hello World") == "hello-world"
    assert _slugify_romanji("Test 123") == "test-123"


def test_output_is_always_ascii():
    """_slugify_romanji output is always ASCII — no non-ASCII characters leak through."""
    test_inputs = [
        "テスト",
        "てすと",
        "新聞",
        "東京ニュース",
        "気-news",
        "日本語",
        "Hello World",
        "Test 123",
        "かきくけこ",
        "シャシユショ",
        "ちゃっちゅちょ",
        "ぎゃぎゅぎょ",
        "ぴゃぴゅぴょ",
        "日本語テスト",
        "日本語新聞",
        "テスト日本語",
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    ]
    for title in test_inputs:
        result = _slugify_romanji(title)
        assert result.isascii(), (
            f"_slugify_romanji('{title}') returned non-ASCII: {repr(result)}"
        )


def test_output_has_no_non_alphanumeric_except_dash():
    """Output contains only alphanumeric characters and dashes."""
    test_inputs = [
        "テスト",
        "てすと",
        "東京ニュース",
        "気-news",
        "Hello World",
        "Test 123",
        "かきくけこ",
        "シャシユショ",
        "ちゃっちゅちょ",
        "ぎゃぎゅぎょ",
        "ぴゃぴゅぴょ",
        "日本語テスト",
        "日本語新聞",
        "テスト日本語",
    ]
    for title in test_inputs:
        result = _slugify_romanji(title)
        assert all(c.isalnum() or c == "-" for c in result), (
            f"_slugify_romanji('{title}') produced non-alphanumeric char: "
            f"{repr(result)}"
        )
