# https://en.wikipedia.org/wiki/ANSI_escape_code#Colors

# Windows XP CMD normal colors
ansi_dark = [
    [  0,   0,   0], # black
    [128,   0,   0], # red
    [  0, 128,   0], # green
    [128, 128,   0], # brown/yellow
    [  0,   0, 128], # blue
    [128,   0, 128], # magenta
    [  0, 128, 128], # cyan
    [192, 192, 192], # gray
]

# Windows XP CMD light colors
ansi_light = [
    [ 85,  85,  85], # dark gray
    [255,  85,  85], # red
    [ 85, 255,  85], # green
    [255, 255,  85], # yellow
    [ 85,  85, 255], # blue
    [255,  85, 255], # magenta
    [ 85, 255, 255], # cyan
    [255, 255, 255], # white
]

# Miscellaneous colors
misc = [
    [0, 0, 255],
]


def clamp(lower, upper, value):
    return max(lower, min(upper, value))


def yuv(r, g, b):
    y = clamp(0, 255, int( 0.183 * r + 0.614 * g + 0.062 * b +  16.0))
    u = clamp(0, 255, int(-0.101 * r - 0.338 * g + 0.439 * b + 128.0))
    v = clamp(0, 255, int( 0.439 * r - 0.399 * g - 0.040 * b + 128.0))
    return [ y, u, v ]


def convert_colors(label, colors):
    print(label)
    for r, g, b in colors:
        y, u, v = yuv(r, g, b)
        uyvy = (y << 24) | (v << 16) | (y << 8) | u
        print(f"0x{uyvy:08x} : {u:3} {y:3} {v:3} {y:3}")


if __name__ == "__main__":
    convert_colors("ansi_dark", ansi_dark)
    convert_colors("ansi_light", ansi_light)
    convert_colors("misc", misc)
