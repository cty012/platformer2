import utils.stopwatch as sw
import utils.fonts as f
import utils.functions as utils


class Clock:
    def __init__(self, pos):
        self.pos = pos  # (120, 90)
        self.stopwatch = sw.Stopwatch()
        self.text_img = None
        self.text_width = 0
        self.small_text_img = None
        self.small_text_width = 0

    def show(self, ui, *, time=None):
        # get text img
        if self.text_img is None:
            self.text_img = {str(c): ui.get_text_img(str(c), f.digital_7(50)) for c in list(range(10)) + [':']}
            self.text_width = self.text_img['0'].get_size()[0]
            self.small_text_img = {str(c): ui.get_text_img(str(c), f.digital_7(30)) for c in list(range(10)) + [':']}
            self.small_text_width = self.small_text_img['0'].get_size()[0]
        # show time
        current_time = self.stopwatch.get_str_time().split(':') if time is None else time
        # show minutes
        pos = [self.pos[0] - 10, self.pos[1]]
        for digit in reversed(current_time[0]):
            ui.show_img(pos, self.text_img[digit], align=(2, 2))
            pos[0] -= self.text_width
        # show ':'
        ui.show_img(self.pos, self.text_img[':'], align=(1, 2))
        # show seconds
        pos = [self.pos[0] + 10, self.pos[1]]
        for digit in current_time[1]:
            ui.show_img(pos, self.text_img[digit], align=(0, 2))
            pos[0] += self.text_width
        # show < 1 second
        pos = [self.pos[0] + 65, self.pos[1]]
        for digit in current_time[2]:
            ui.show_img(pos, self.small_text_img[digit], align=(0, 2))
            pos[0] += self.small_text_width
