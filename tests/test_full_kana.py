from KeiNews.main import _katakana_to_hiragana

text = "ニュース"
print(f"Input: {text}")
hira = _katakana_to_hiragana(text)
print(f"Hiragana: {hira}")
for c in hira:
    print(f"Char: {c}, Codepoint: {ord(c)}")
