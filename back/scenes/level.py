import back.sprites.component as c
import utils.fonts as f
import utils.score_reader as sr
import utils.functions as utils


class Scene:
    def __init__(self, args):
        self.args = args
        self.pos = (0, 0)
        self.background = c.Component(lambda ui: ui.show_div((0, 0), self.args.size, color=(60, 179, 113)))
        self.buttons = {
            '1': c.Button((240, 250), (80, 120), '1', font=f.tnr(25), align=(1, 1), background=(210, 210, 210)),
            '2': c.Button((440, 250), (80, 120), '2', font=f.tnr(25), align=(1, 1), background=(210, 210, 210)),
            '3': c.Button((640, 250), (80, 120), '3', font=f.tnr(25), align=(1, 1), background=(210, 210, 210)),
            '4': c.Button((840, 250), (80, 120), '4', font=f.tnr(25), align=(1, 1), background=(210, 210, 210)),
            '5': c.Button((1040, 250), (80, 120), '5', font=f.tnr(25), align=(1, 1), background=(210, 210, 210)),
            '6': c.Button((240, 400), (80, 120), '6', font=f.tnr(25), align=(1, 1), background=(210, 210, 210)),
            '7': c.Button((440, 400), (80, 120), '7', font=f.tnr(25), align=(1, 1), background=(210, 210, 210)),
            '8': c.Button((640, 400), (80, 120), '8', font=f.tnr(25), align=(1, 1), background=(210, 210, 210)),
            '9': c.Button((840, 400), (80, 120), '9', font=f.tnr(25), align=(1, 1), background=(210, 210, 210)),
            '10': c.Button((1040, 400), (80, 120), '10', font=f.tnr(25), align=(1, 1), background=(210, 210, 210)),
            'mode': c.Button(
                (self.args.size[0] // 2, 540), (200, 60), 'single player',
                font=f.tnr(20), align=(1, 1), background=(210, 210, 210)
            ),
            'back': c.Button(
                (self.args.size[0] // 2, 640), (600, 80), 'Back',
                font=f.tnr(25), align=(1, 1), background=(210, 210, 210)
            ),
        }
        self.scores = sr.ScoreReader.load(args.save_path)

    def process_events(self, events):
        if events['mouse-left'] == 'down':
            for name in self.buttons:
                if self.buttons[name].in_range(events['mouse-pos']):
                    return self.execute(name)
        return [None]

    def execute(self, name):
        if name in map(str, range(1, 11)):
            mode = {'single player': 'sing', 'multiplayer': 'mult'}[self.buttons['mode'].text]
            if mode == 'sing':
                return ['game', {'open': 'new', 'mode': 'sing', 'level': name}]
            elif mode == 'mult':
                return ['room_server', {'open': 'new', 'mode': 'mult', 'level': name}]
        elif name == 'mode':
            button = self.buttons['mode']
            button.text = {'single player': 'multiplayer', 'multiplayer': 'single player'}[button.text]
        elif name == 'back':
            return ['menu']
        return [None]

    def show(self, ui):
        self.background.show(ui)
        ui.show_text((self.args.size[0] // 2, 100), "Select A Level", font=f.cambria(60), align=(1, 1))
        for name in self.buttons:
            button = self.buttons[name]
            button.show(ui)
            if name not in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
                continue
            if self.scores[name][0] < 0:
                continue
            b_pos = button.pos[0] + button.size[0] // 2, button.pos[1] + button.size[1] // 2
            # show score
            x, y = 35, 50
            pos_list = [[b_pos[0] - x, b_pos[1] + y], [b_pos[0], b_pos[1] + y], [b_pos[0] + x, b_pos[1] + y]]
            for i, pos in enumerate(pos_list):
                ui.show_div(pos, (24, 24), color=(255, 215, 0) if self.scores[name][0] > i else (255, 255, 255), align=(1, 1))
                ui.show_div(pos, (24, 24), border=2, align=(1, 1))
            # show time
            if self.scores[name][1] is None:
                continue
            ui.show_div((b_pos[0] + 23, b_pos[1] - 50), (80, 26), color=(255, 255, 255), align=(1, 1))
            ui.show_div((b_pos[0] + 23, b_pos[1] - 50), (80, 26), border=2, align=(1, 1))
            time = utils.to_str_time(self.scores[name][1]).split(':')
            ui.show_text((b_pos[0] + 38, b_pos[1] - 40), f'{time[0]}:{time[1]}', f.get_font('04b_03b', 18), align=(2, 2))
            ui.show_text((b_pos[0] + 41, b_pos[1] - 41), f'{time[2]}', f.get_font('04b_03b', 14), align=(0, 2))
