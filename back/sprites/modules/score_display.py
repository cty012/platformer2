import utils.fonts as f


class ScoreDisplay:
    def __init__(self, pos):
        self.pos = pos
        self.text_img = {}

    def show(self, ui, *, score=0):
        if str(score) not in self.text_img.keys():
            self.text_img[str(score)] = ui.get_text_img(str(score), f.get_font('04b_03b', 30))
        ui.show_div((self.pos[0] + 4, self.pos[1] + 4), (28, 28), color=(255, 179, 0), align=(0, 1))
        ui.show_div(self.pos, (28, 28), color=(255, 215, 0), align=(0, 1))
        ui.show_img((self.pos[0] + 60, self.pos[1] + 2), self.text_img[str(score)], align=(0, 1))
