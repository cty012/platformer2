import random
import re


# return the top-left corner of the rectangle
def top_left(pos, size, *, align=(0, 0)):
    return pos[0] - align[0] * (size[0] // 2), pos[1] - align[1] * (size[1] // 2)


# whether two rectangles overlap
def overlap(rect1, rect2):
    return is_rect([rect1[0], rect2[1]]) and is_rect([rect2[0], rect1[1]])


def direction(rect1, rect2, direct):
    if max(rect1[0][direct], rect1[1][direct]) <= min(rect2[0][direct], rect2[1][direct]):
        return 'low'
    elif min(rect1[0][direct], rect1[1][direct]) >= max(rect2[0][direct], rect2[1][direct]):
        return 'high'
    return None


def is_rect(rect):
    return rect[0][0] < rect[1][0] and rect[0][1] < rect[1][1]


def random_color():
    return [random.randint(0, 255) for _ in range(3)]


def is_ip(ip):
    regex = r'(([1-9]?[0-9])|(1[0-9][0-9])|(2[0-4][0-9])|(25[0-5]))'
    return re.match(r'^(' + regex + r'\.){3}' + regex + r'$', ip)


def is_private_ip(ip):
    if not is_ip(ip):
        return False
    return ip.startswith('10.') or ip.startswith('192.168.') or re.match(r'^172\.((1[6-9])|(2[0-9])|(3[0-1]))\.', ip)


def to_str_time(hundredth_secs, *, connect=(':', ':')):
    minutes = hundredth_secs // 6000
    seconds = (hundredth_secs % 6000) // 100
    decimals = hundredth_secs % 100
    return f'{minutes:02}{connect[0]}{seconds:02}{connect[1]}{decimals:02}'
