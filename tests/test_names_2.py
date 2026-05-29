from KeiNews.main import _katakana_to_hiragana
hira = _katakana_to_hiragana("ジャパン")
print(f"Hiragana: {hira}")
for c in hira:
    print(f"Char: {c}")
