import json
import os

import back.sprites.component as c
import back.sprites.menu.game_menu as gm
import back.sprites.menu.saver as s
import back.sprites.menu.score_board as sb
import utils.fonts as f
import utils.stopwatch as sw


class Scene:
    def __init__(self, args, mode):
        self.args = args
        self.background = c.Component(lambda ui: ui.show_div((0, 0), self.args.size, color=(60, 179, 113)))
        # mode and game
        self.mode = mode
        self.game = None
        if mode['mode'] == 'mult' and mode['connect']['identity'] == 'client':
            import back.sprites.game_client as g
        else:
            import back.sprites.game as g
        with open(os.path.join('levels', f'{self.mode["level"]}.json')) as file:
            self.game = g.Game(self.args, self.mode, json.load(file))
        # others
        self.timer = sw.Stopwatch()
        self.timer.start()
        self.game_menu = gm.GameMenu((self.args.size[0] // 2, self.args.size[1] // 2), align=(1, 1))
        self.saver = s.Saver(self.args, msg=self.game.name)
        self.score_board = sb.ScoreBoard((self.args.size[0] // 2, self.args.size[1] // 2), align=(1, 1))

    def process_events(self, events):
        # game ended
        if self.game.win is not None:
            if self.timer.is_running():
                self.timer.stop()
            return self.execute(self.score_board.process_events(events))
        # game paused
        elif self.game_menu.active:
            return self.execute(self.game_menu.process_events(events))
        # pause game
        elif 'escape' in events['key-down'] and not (self.mode['mode'] == 'mult' and self.mode['connect']['identity'] == 'client'):
            return self.execute('continue')
        # play game
        return self.execute(self.game.process_events(events))

    def execute(self, name):
        if name == 'continue':
            if self.mode['mode'] == 'mult' and self.mode['connect']['identity'] == 'server':
                self.game.send('pause')
            self.game_menu.active = not self.game_menu.active
            if self.timer.is_running():
                self.timer.stop()
            else:
                self.timer.start()
        elif name == 'quit':
            self.game.close_socket()
            return ['menu']
        return [None]

    def show(self, ui):
        self.background.show(ui)
        self.game.show(ui)
        # show timer
        current_time = self.timer.get_str_time().split(':')
        print(current_time)
        ui.show_text((self.args.size[0] // 2 - 10, 120), current_time[0], f.cambria(35), align=(2, 1))
        ui.show_text((self.args.size[0] // 2, 120), ':', f.cambria(35), align=(1, 1))
        ui.show_text((self.args.size[0] // 2 + 10, 120), current_time[1], f.cambria(35), align=(0, 1))
        if self.game.win is not None:
            self.score_board.show(ui, self.game.win, self.game.score)
        if self.game_menu.active:
            self.game_menu.show(ui)
