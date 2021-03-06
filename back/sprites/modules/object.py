import utils.functions as utils


class Object:
    def __init__(self, info, type):
        # info
        self.type = type
        self.name = info['name']
        # show
        self.pos = [0, 0]
        self.size = info['size']
        self.color = info['color']
        # move
        self.speed = [0, 0]
        # update
        self.update = []

    def get_rect(self, *, pan=(0, 0)):
        return [
            [self.pos[0] + pan[0], self.pos[1] + pan[1]],
            [self.pos[0] + self.size[0] + pan[0], self.pos[1] + self.size[1] + pan[1]]
        ]

    def get_orig_rect(self, *, pan=(0, 0)):
        return [
            [self.pos[0] - self.speed[0] + pan[0], self.pos[1] - self.speed[1] + pan[1]],
            [self.pos[0] + self.size[0] - self.speed[0] + pan[0], self.pos[1] + self.size[1] - self.speed[1] + pan[1]]
        ]

    def in_range(self, pos, *, pan=(0, 0)):
        rect = self.get_rect(pan=pan)
        return rect[0][0] < pos[0] < rect[1][0] and rect[0][1] < pos[1] < rect[1][1]

    def get_status(self):
        return {param: eval(f'self.{param}', {'self': self}) for param in self.update}

    def set_status(self, status):
        for param in self.update:
            exec(f'self.{param} = status[\'{param}\']')

    def show(self, ui, *, pan=(0, 0)):
        ui.show_div(self.pos, self.size, color=self.color, pan=pan)


class Static(Object):
    def __init__(self, info, *, type='static', align=(0, 0)):
        super().__init__(info, type)
        self.pos = list(utils.top_left(info['pos'], info['size'], align=align))
        if 'update' in info.keys():
            self.update = info['update']


class Movable(Object):
    def __init__(self, info, *, type='movable', align=(0, 0)):
        super().__init__(info, type)
        # show
        self.pos = list(utils.top_left(info['track'][0]['pos'], info['size'], align=align))
        # move
        self.track = info['track']
        self.update_speed = True
        self.speed = self.track[0]['speed']
        # update
        if 'update' in info.keys():
            self.update = info['update']

    def move(self):
        if self.update_speed:
            for point in self.track:
                if point['pos'] == self.pos:
                    self.speed = point['speed']
        self.pos[0] += self.speed[0]
        self.pos[1] += self.speed[1]
        self.update_speed = True


class Switch(Object):
    def __init__(self, info, *, type='switch', align=(0, 0)):
        super().__init__(info, type)
        self.pos = list(utils.top_left(info['pos'], info['size'], align=align))
        # command
        self.command = info['command']
        self.state = 'close'
        self.triggered = False
        # move
        self.speed = [0, 0]
        # update
        self.update = []
        if 'update' in info.keys():
            self.update = info['update']

    def auto(self, map, players):
        if self.triggered:
            self.triggered = False
            return
        if 'auto' not in self.command.keys():
            return
        for command in self.command['auto']:
            self.execute(map, players, command)

    def trigger(self, map, players):
        self.triggered = True
        for command in self.command[self.state]:
            self.execute(map, players, command)

    def compare(self, map, players, command):
        if command[0] == 'color':
            return self.color == command[1]
        elif command[0] == 'exist':
            return len(map.find_objects(command[1])) > 0
        elif command[0] == 'player':
            player = players[command[1]]
            return eval(f'player.{command[2]} == {command[3]}')
        elif command[0] == 'object':
            for obj in map.find_objects(command[1]):
                if eval(f'obj.{command[2]} == {command[3]}'):
                    return True
            return False

    def execute(self, map, players, command):
        if command[0] == 'state':
            self.state = command[1]
        elif command[0] == 'color':
            self.color = command[1]
        elif command[0] == 'remove':
            map.remove_objects(command[1])
        elif command[0] == 'player':
            player = players[command[1]]
            exec(f'player.{command[2]} = {command[3]}')
        elif command[0] == 'object':
            for obj in map.find_objects(command[1]):
                exec(f'obj.{command[2]} = {command[3]}')
        elif command[0] == 'if':
            if self.compare(map, players, command[1]):
                for com in command[2]:
                    self.execute(map, players, com)
