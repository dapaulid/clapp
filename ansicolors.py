import sys

COLOR_CODES = {
#    name                FG  BG
    'black'           : (30, 40),
    'red'             : (31, 41),
    'green'           : (32, 42),
    'yellow'          : (33, 43),
    'blue'            : (34, 44),
    'magenta'         : (35, 45),
    'cyan'            : (36, 46),
    'white'           : (37, 47),
    'bright_black'    : (90, 100),
    'bright_red'      : (91, 101),
    'bright_green'    : (92, 102),
    'bright_yellow'   : (93, 103),
    'bright_blue'     : (94, 104),
    'bright_magenta'  : (95, 105),
    'bright_cyan'     : (96, 106),
    'bright_white'    : (97, 107),
}

#aliases
COLOR_CODES['gray'] = COLOR_CODES['bright_black']

STYLE_CODES = {
    'reset'           : 0,
    'bold'            : 1,
    'faint'           : 2,
    'italic'          : 3,
    'underlined'       : 4,
    'blink_slow'      : 5,
    'blink_rapid'     : 6,
    'inverted'        : 7,
    'conceal'         : 8,
    'crossed'         : 9,
}

ESCAPE = '\x1B[{0}m'

RESET = ESCAPE.format(0) 

def color(fg = None, bg = None, style = None):
    codes = []
    if fg is not None:
        codes.append(str(COLOR_CODES[fg][0]))
    # end if
    if bg is not None:
        codes.append(str(COLOR_CODES[bg][1]))
    # end if
    if style is not None:
        codes.append(str(STYLE_CODES[style]))
    # end if    
    return ESCAPE.format(';'.join(codes))
# end function

def use_colors():
    return sys.stdout.isatty()
# end function

def colorize(str, fg = None, bg = None, style = None):
    return color(fg, bg, style) + str + RESET if use_colors() else str
# end function

def set_color(fg = None, bg = None, style = None):
    if not use_colors():
        return
    # end if
    sys.stdout.write(color(fg, bg, style))
    sys.stdout.flush()
# end function

def reset_color():
    if not use_colors():
        return
    # end if
    sys.stdout.write(RESET)
    sys.stdout.flush()
# end function