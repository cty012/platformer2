import back.sprites.component as c
import utils.fonts as f
from utils import settings
import utils.stopwatch as sw


class Scene:
    def __init__(self, args):
        self.args = args
        self.background = c.Component(lambda ui: ui.show_div((0, 0), self.args.size, color=(60, 179, 113)))
        self.buttons = {
            'new': c.Button(
                (self.args.size[0] // 2, 360), (600, 80), 'New Game',
                font=f.tnr(25), align=(1, 1), background=(210, 210, 210)
            ),
            'join': c.Button(
                (self.args.size[0] // 2, 460), (600, 80), 'Join Game',
                font=f.tnr(25), align=(1, 1), background=(210, 210, 210)
            ),
            'quit': c.Button(
                (self.args.size[0] // 2, 560), (600, 80), 'Exit',
                font=f.tnr(25), align=(1, 1), background=(210, 210, 210)
            ),
            'reload_settings': c.Button(
                (self.args.size[0] - 140, self.args.size[1] - 3), (280, 30), '>> Reload settings <<',
                font=f.get_font('courier-prime', 20), align=(1, 2),
                color=(None, (255, 255, 255)), background=None, border=1
            )
        }
        self.settings_reloaded = False
        self.timer = sw.Stopwatch()

    def process_events(self, events):
        if self.settings_reloaded and self.timer.get_time() >= 1:
            self.settings_reloaded = False
            self.timer.stop()
            self.timer.clear()
        if events['mouse-left'] == 'down':
            for name in self.buttons:
                if self.buttons[name].in_range(events['mouse-pos']):
                    return self.execute(name)
        return [None]

    def execute(self, name):
        if name == 'new':
            return ['level']
        elif name == 'join':
            return ['join']
        elif name == 'save':
            return ['save']
        elif name == 'quit':
            return ['quit']
        elif name == 'reload_settings':
            settings.load()
            self.settings_reloaded = True
            self.timer.start()
        return [None]

    def show(self, ui):
        self.background.show(ui)
        ui.show_texts((self.args.size[0] // 2, 150), [["PLATFORMER", (0, 0, 0)]], f.cambria(120), align=(1, 1))
        for name in self.buttons:
            self.buttons[name].show(ui)
        if self.settings_reloaded:
            ui.show_text(
                (self.args.size[0] - 140, self.args.size[1] - 43), "Settings reloaded!",
                f.get_font('courier-prime', 20), color=(64, 64, 255), align=(1, 2)
            )
