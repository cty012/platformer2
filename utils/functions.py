# return the top-left corner of the rectangle
def top_left(pos, size, *, align=(0, 0)):
    return pos[0] - align[0] * (size[0] // 2), pos[1] - align[1] * (size[1] // 2)


# whether two rectangles overlap
def overlap(rect1, rect2):
    return is_rect([rect1[0], rect2[1]]) and is_rect([rect2[0], rect1[1]])


def direction(rect1, rect2, direction):
    if max(rect1[0][direction], rect1[1][direction]) <= min(rect2[0][direction], rect2[1][direction]):
        return 'low'
    elif min(rect1[0][direction], rect1[1][direction]) >= max(rect2[0][direction], rect2[1][direction]):
        return 'high'
    return None


def is_rect(rect):
    return rect[0][0] < rect[1][0] and rect[0][1] < rect[1][1]
