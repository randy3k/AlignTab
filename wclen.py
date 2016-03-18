# import from https://github.com/vkocubinsky/SublimeTableEditor/blob/master/widechar_support.py
wide_char_ranges = [
    # http://en.wikipedia.org/wiki/Han_unification
    (0x4E00, 0x9FFF),
    (0x3400, 0x4DBF),
    (0xF900, 0xFAFF),
    (0x2E80, 0x2EFF),
    (0x3000, 0x303F),
    (0x31C0, 0x31EF),
    (0x2FF0, 0x2FFF),
    (0x2F00, 0x2FDF),
    (0x3200, 0x32FF),
    (0x3300, 0x33FF),
    (0xF900, 0xFAFF),
    (0xFE30, 0xFE4F),
    # See http://en.wikipedia.org/wiki/Hiragana
    (0x3040, 0x309F),
    # See http://en.wikipedia.org/wiki/Katakana
    (0x30A0, 0x30FF),
    # See http://en.wikipedia.org/wiki/Hangul
    (0xAC00, 0xD7AF),
    (0x1100, 0x11FF),
    (0x3130, 0x318F),
    (0x3200, 0x32FF),
    (0xA960, 0xA97F),
    (0xD7B0, 0xD7FF),
    (0XFF00, 0XFFEF),
    # See http://en.wikipedia.org/wiki/Kanbun
    (0x3190, 0x319F),
    # See http://en.wikipedia.org/wiki/Halfwidth_and_Fullwidth_Forms
    (0xFF00, 0xFFEF),
]


def _in_range(c):
    c = ord(c)
    return any(r[0] <= c <= r[1] for r in wide_char_ranges)


def wclen(s):
    return sum(2 if _in_range(c) else 1 for c in s)
