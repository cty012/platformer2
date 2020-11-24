import json
import socket
from threading import Thread

import back.sprites.modules.clock as c
import back.sprites.modules.map as m
import back.sprites.modules.player as p
import back.sprites.modules.score_display as sd
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
        # pan
        self.target_pan = None
        self.pan = None
        self.alpha = None
        # ping
        if self.mode['mode'] == 'mult':
            self.pingstamp = [0] * (len(self.mode['connect']['clients']) + 1)
        else:
            self.pingstamp = [0]  # failsafe
        # thread
        self.thread_recv = []
        self.connected = {'connected': True}
        self.prepare()
        # others
        self.clock = c.Clock((120, 90))
        self.clock.stopwatch.start()
        self.score_display = sd.ScoreDisplay((70, 150))

########################################################################################################################
# PREPARATION #
########################################################################################################################
    def prepare(self):
        self.map = m.Map(self.mode, self.level_info['map'], (0, self.args.size[1]), align=(0, 2))
        if self.mode['mode'] == 'mult':
            self.players = [p.Player(self.level_info['player'], i) for i in range(len(self.mode['connect']['clients']) + 1)]
        elif self.mode['mode'] == 'sing':
            self.players = [p.Player(self.level_info['player'])]
        self.my_player = self.players[0]
        self.target_pan = self.get_target_pan()
        self.pan = self.target_pan
        self.alpha = 10
        # thread
        if self.mode['mode'] == 'mult':
            for i in range(len(self.mode['connect']['clients'])):
                new_thread = Thread(target=self.receive(i), name=f'recv-{i}', daemon=True)
                self.thread_recv.append(new_thread)
                new_thread.start()

########################################################################################################################
# EVENTS #
########################################################################################################################
    def process_events(self, events):
        # player collect coins and switches
        for player in self.players:
            # collect coins
            for coin in self.map.objects['coin']:
                if player.will_collide_with(coin):
                    self.score += 1
                    self.map.remove_objects(coin.name)
            # trigger switches
            for switch in self.map.objects['switch']:
                if player.will_collide_with(switch):
                    switch.trigger(self.map, self.players)
        for switch in self.map.objects['switch']:
            switch.auto(self.map, self.players)
        # move elevators
        for elevator in self.map.objects['elevator']:
            elevator.move()
        # move monsters
        for monster in self.map.objects['monster']:
            monster.move()
        # move my player
        self.my_player.process_pressed(events['key-pressed'], events['key-down'])
        for player in self.players:
            player.move(self.map)
        # update displaying window
        self.refresh_pan()
        # check winning conditions
        self.check_win()
        # send data to clients
        if self.mode['mode'] == 'mult' and self.connected['connected']:
            self.send(json.dumps(self.get_status()))
            self.send('time' + self.clock.stopwatch.get_str_time())
        if self.win is not None:
            self.close_client_sockets()
            self.connected['connected'] = False

    def send(self, msg):
        try:
            for client in self.mode['connect']['clients']:
                msg_b = bytes(msg, encoding='utf-8')
                client['socket'].sendall(bytes(f'{len(msg_b):10}', encoding='utf-8'))
                client['socket'].sendall(msg_b)
        except OSError as e:
            print(e)

    def receive(self, i):
        def func():
            parser = Parser()
            client = self.mode['connect']['clients'][i]
            print(f'SERVER START receiving FROM C{i}...')
            while self.connected['connected']:
                try:
                    events_strs = parser.parse(client['socket'].recv(1 << 20))
                except socket.timeout:
                    continue
                except json.decoder.JSONDecodeError:
                    print('\tJSON Decode Error!')
                    continue
                except ConnectionResetError:
                    print('Connection Reset by CLIENT')
                    break
                for events_str in events_strs:
                    events = json.loads(events_str)
                    self.players[i + 1].process_pressed(events['key-pressed'], events['key-down'])
                    self.pingstamp[i + 1] = max(self.pingstamp[i + 1], events['ping'])
            print(f'SERVER END receiving FROM C{i}...')
        return func

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

    def check_win(self):
        if self.win is not None:
            return
        for player in self.players:
            # reach target -> WIN
            for target in self.map.objects['target']:
                if player.collide_with(target):
                    self.win = True
                    return
        for player in self.players:
            # squeezed to zero -> LOSE
            if player.size[0] * player.size[1] == 0:
                self.win = False
                return
            # fall -> LOSE
            if player.pos[1] > self.map.size[1] + 300:
                self.win = False
                return
            # touch monster -> LOSE
            for monster in self.map.objects['monster']:
                if player.collide_with(monster):
                    self.win = False
                    return

    def close_client_sockets(self):
        if self.mode['mode'] == 'sing':
            return
        self.send('close')

    def close_socket(self):
        self.connected['connected'] = False
        if self.mode['mode'] == 'sing':
            return
        self.mode['connect']['socket'].close()

########################################################################################################################
# DISPLAY #
########################################################################################################################
    def get_status(self):
        return {
            'win': self.win,
            'score': self.score,
            'map': self.map.get_status(),
            'players': [player.get_status() for player in self.players],
            'pings': self.pingstamp
        }

    def show(self, ui):
        # show map
        self.map.show(ui, pan=self.pan)
        # show player
        for player in reversed(self.players):
            player.show(ui, pan=self.pan)
        # show timer
        self.clock.show(ui)
        # show score
        self.score_display.show(ui, score=self.score)
