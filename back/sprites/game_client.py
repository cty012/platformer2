import json
import socket
import time
from threading import Thread

import back.sprites.modules.clock as c
import back.sprites.modules.map as m
import back.sprites.modules.player as p
import back.sprites.modules.score_display as sd
import utils.fonts as f
from utils.parser import Parser
from utils import settings


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
        # ping
        self.pingstamp = time.perf_counter_ns()
        self.pingdelta = 0
        # thread
        self.thread_recv = None
        self.connected = {'connected': True}
        self.prepare()
        # time
        self.time = '00:00:00'
        self.clock = c.Clock((120, 90))
        self.score_display = sd.ScoreDisplay((70, 150))

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
        # Optional animation lag-smoothing
        if settings.get('animation_lag_smoothing'):
            for object_type in ['elevator', 'monster']:
                for obj in self.map.objects[object_type]:
                    obj.move()
            self.my_player.process_pressed(events['key-pressed'], events['key-down'])
            self.my_player.move(self.map)
        # ALWAYS remember to refresh panning
        self.refresh_pan()
        # send data
        if self.connected['connected']:
            self.send(events)

    def send(self, events):
        try:
            operations = bytes(
                json.dumps({'key-pressed': events['key-pressed'], 'key-down': events['key-down'], 'ping': self.incr_ping()}),
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
                    self.connected['connected'] = False
                    self.win = 'draw'
                # update status
                elif msg.startswith('time'):
                    self.time = msg[4:]
                else:
                    status = json.loads(msg)
                    self.set_status(status)
        print('CLIENT END receiving...')

########################################################################################################################
# OPERATIONS #
########################################################################################################################
    def get_target_pan(self):
        pos, size, screen_size, map_size = self.my_player.pos, self.my_player.size, self.args.size, self.map.size
        pos = (pos[0] + size[0] // 2, pos[1] + size[1] // 2)
        pan = pos[0] - screen_size[0] // 2, pos[1] - screen_size[1] // 2
        # check boundaries
        pan = max(pan[0], 0), max(pan[1], 0)
        pan = min(pan[0], map_size[0] - screen_size[0]), min(pan[1], map_size[1] - screen_size[1])
        return -pan[0], -pan[1]

    def refresh_pan(self):
        self.target_pan = self.get_target_pan()
        self.pan = (
            round((self.pan[0] * (self.alpha - 1) + self.target_pan[0]) / self.alpha),
            round((self.pan[1] * (self.alpha - 1) + self.target_pan[1]) / self.alpha)
        )

    def close_socket(self):
        if self.mode['mode'] == 'sing':
            return
        try:
            self.mode['connect']['socket'].shutdown(0)
        except OSError as e:
            print(e)
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

        self.pingdelta = self.pingstamp - status['pings'][self.mode['connect']['id']]

    def show(self, ui):
        # show map
        self.map.show(ui, pan=self.pan)
        # show player
        for player in reversed(self.players):
            if player != self.my_player:
                player.show(ui, pan=self.pan)
        self.my_player.show(ui, pan=self.pan)
        # show timer
        self.clock.show(ui, time=self.time.split(':'))
        # show score
        self.score_display.show(ui, score=self.score)
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
        # Show ping
        ui.show_text(
            (self.args.size[0] - 10, 10), f"Latency: {round(self.pingdelta/1e6):6d} ms",
            font=f.get_font('courier-prime', 20), color=self.__class__.get_ping_color(self.pingdelta/1e6), align=(2, 0)
        )

########################################################################################################################
# PING #
########################################################################################################################
    def ping_incr(self):
        p = self.pingstamp
        self.pingstamp = time.perf_counter_ns()
        return p
    def incr_ping(self):
        self.pingstamp = time.perf_counter_ns()
        return self.pingstamp

    @classmethod
    def get_ping_color(cls, ping):
        if ping < settings.get('lag_ping_threshold'):
            return (255, 255, 255)
        return (255, 100, 100)
