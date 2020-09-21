def get_font(font_name, font_size):
    return eval(font_name)(font_size)


# times new roman
def tnr(font_size):
    return 'src', 'timesnewroman.ttf', font_size


# cambria
def cambria(font_size):
    return 'src', 'cambria.ttf', font_size


def cheri(font_size):
    return 'src', 'cheri.ttf', font_size


def digital_7(font_size):
    return 'src', 'digital-7.ttf', font_size
