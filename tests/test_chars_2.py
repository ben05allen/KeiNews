text = "東京ニュース"
for c in text:
    print(f"'{c}' ({hex(ord(c))}) -> {'isascii' if c.isascii() else 'non-ascii'}")
