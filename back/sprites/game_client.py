import json
import socket
from threading import Thread

import back.sprites.modules.map as m
import back.sprites.modules.player as p
import utils.fonts as f
from utils.parser import Parser


class Game:
    def __init__(self, args, mode, level_info):
        self.args = args
        self.mode = mode
        self.level_info = level_info
        self.name = ''
        self.win = None
        self.score = 0
        # modules
        self.map = None
        self.players = None
        self.my_player = None
        # ui
        self.paused = False
        self.target_pan = None
        self.pan = None
        self.alpha = None
        # thread
        self.thread_recv = None
        self.connected = {'connected': True}
        self.prepare()
        # time
        self.time = '00:00:00'

########################################################################################################################
# PREPARATION #
########################################################################################################################
    def prepare(self):
        self.map = m.Map(self.mode, self.level_info['map'], (0, self.args.size[1]), align=(0, 2))
        self.players = [p.Player(self.level_info['player'], i) for i in range(self.mode['connect']['total'])]
        self.my_player = self.players[self.mode['connect']['id']]
        self.target_pan = self.get_target_pan()
        self.pan = self.target_pan
        self.alpha = 10
        # thread
        self.thread_recv = Thread(target=self.receive, name=f'recv', daemon=True)
        self.thread_recv.start()

########################################################################################################################
# EVENTS #
########################################################################################################################
    def process_events(self, events):
        if self.connected['connected']:
            self.send(events)

    def send(self, events):
        try:
            operations = bytes(
                json.dumps({'key-pressed': events['key-pressed'], 'key-down': events['key-down']}),
                encoding='utf-8'
            )
            self.mode['connect']['socket'].send(bytes(f'{len(operations):10}', encoding='utf-8'))
            self.mode['connect']['socket'].send(operations)
        except OSError:
            pass

    def receive(self):
        parser = Parser()
        print('CLIENT START receiving...')
        while self.connected['connected']:
            # receive messages
            try:
                msgs = parser.parse(self.mode['connect']['socket'].recv(1 << 20))
            except socket.timeout:
                continue
            except OSError:
                break
            # process the messages
            for msg in msgs:
                if msg == 'pause':
                    self.paused = not self.paused
                # close socket
                elif msg == 'close':
                    continue
                # update status
                elif msg.startswith('time'):
                    self.time = msg[4:]
                else:
                    status = json.loads(msg)
                    self.set_status(status)
            # refresh pan
            self.refresh_pan()
        print('CLIENT END receiving...')

########################################################################################################################
# OPERATIONS #
########################################################################################################################
    def get_target_pan(self):
        pos, screen_size, map_size = self.my_player.pos, self.args.size, self.map.size
        pan = pos[0] - screen_size[0] // 2, pos[1] - screen_size[1] // 2
        # check boundaries
        pan = max(pan[0], 0), max(pan[1], 0)
        pan = min(pan[0], map_size[0] - screen_size[0]), min(pan[1], map_size[1] - screen_size[1])
        return -pan[0], -pan[1]

    def refresh_pan(self):
        self.target_pan = self.get_target_pan()
        self.pan = (
            (self.pan[0] * (self.alpha - 1) + self.target_pan[0]) // self.alpha,
            (self.pan[1] * (self.alpha - 1) + self.target_pan[1]) // self.alpha
        )

    def close_socket(self):
        if self.mode['mode'] == 'sing':
            return
        self.mode['connect']['socket'].shutdown(2)
        self.mode['connect']['socket'].close()

########################################################################################################################
# DISPLAY #
########################################################################################################################
    def set_status(self, status):
        self.win = status['win']
        self.score = status['score']
        self.map.set_status(status['map'])
        for i in range(len(self.players)):
            self.players[i].set_status(status['players'][i])
        if self.win is not None:
            print()
            self.connected['connected'] = False

    def show(self, ui):
        self.map.show(ui, pan=self.pan)
        for player in self.players:
            player.show(ui, pan=self.pan)
        # show time
        current_time = self.time.split(':')
        ui.show_text((110, 90), current_time[0], f.digital_7(50), align=(2, 2))
        ui.show_text((120, 90), ':', f.digital_7(50), align=(1, 2))
        ui.show_text((130, 90), current_time[1], f.digital_7(50), align=(0, 2))
        ui.show_text((185, 90), current_time[2], f.digital_7(30), align=(0, 2))
        # show pause message
        if self.paused:
            ui.show_div((self.args.size[0] // 2, self.args.size[1] // 2), (400, 100), color=(192, 192, 192), align=(1, 1))
            ui.show_div(
                (self.args.size[0] // 2, self.args.size[1] // 2), (400, 100),
                color=(0, 0, 0), border=2, align=(1, 1)
            )
            ui.show_text(
                (self.args.size[0] // 2, self.args.size[1] // 2), 'SERVER PAUSED',
                font=f.cambria(30), color=(0, 0, 0), align=(1, 1)
            )
