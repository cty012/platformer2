import utils.fonts as f
import utils.functions as utils


class Player:
    def __init__(self, player_info, id=None):
        # basic info
        self.id = id
        self.id_img = None
        self.pos = player_info['pos']
        self.size = player_info['size']
        self.color = player_info['color']
        # movement
        self.speed = [0, 0]
        self.gravity = [0, 2]
        # status
        self.reference_frame = None
        self.ground = False
        self.jump_times = 0

    def get_rect(self):
        return [[self.pos[0], self.pos[1]], [self.pos[0] + self.size[0], self.pos[1] + self.size[1]]]

    def get_moving_rect(self, target_pos):
        return [
            [min(self.pos[0], target_pos[0]), min(self.pos[1], target_pos[1])],
            [max(self.pos[0], target_pos[0]) + self.size[0], max(self.pos[1], target_pos[1]) + self.size[1]]
        ]

    def process_pressed(self, pressed, down):
        self.sync()
        if 'a' in pressed or 'left' in pressed:
            self.speed[0] -= 8
        if 'd' in pressed or 'right' in pressed:
            self.speed[0] += 8
        if 'w' in down or 'space' in down or 'up' in down:
            if self.ground:
                self.speed[1] = -30
                self.reference_frame = None
                self.ground = False
                self.jump_times = 1
            elif self.jump_times > 0:
                self.speed[1] = -30
                self.jump_times -= 1

    def sync(self):
        if not self.ground:
            self.speed[0] = 0
        else:
            self.speed[0] = self.reference_frame.speed[0]

    def check_obstacles(self, map, magnitude, direction):
        self.ground = False
        # calculate expected position
        pos = self.pos[:]
        pos[direction] += magnitude
        # revise expected position
        for obs in map.objects['obstacle'] + map.objects['elevator']:
            obs_rect = obs.get_rect()
            obs_orig_rect = obs.get_orig_rect()
            if utils.overlap(self.get_moving_rect(pos), obs_rect):
                rel_pos = utils.direction(self.get_rect(), obs_orig_rect, direction)
                # return to the edge
                if rel_pos == 'low' and magnitude >= obs.speed[direction]:
                    pos[direction] = obs_rect[0][direction] - self.size[direction]
                    self.speed[direction] = 0
                    # detect if player is on the ground
                    if direction == 1:
                        self.reference_frame = obs
                        self.ground = True
                        self.jump_times = 1
                elif rel_pos == 'high' and magnitude <= obs.speed[direction]:
                    pos[direction] = obs_rect[1][direction]
                    self.speed[direction] = 0
        return pos

    def collide_with(self, obj):
        return utils.overlap(self.get_rect(), obj.get_rect())

    def move(self, map):
        # move horizontally
        self.pos = self.check_obstacles(map, self.speed[0], 0)
        # move vertically
        self.pos = self.check_obstacles(map, self.speed[1], 1)
        # update speed
        self.speed[1] += self.gravity[1]

    def move_inertia(self, map):
        # move horizontally
        self.pos = self.check_obstacles(map, self.speed[0], 0)
        # move vertically
        self.pos = self.check_obstacles(map, self.speed[1], 1)

    def get_status(self):
        return {'pos': self.pos}

    def set_status(self, status):
        self.pos = status['pos']

    def show(self, ui, *, pan=(0, 0)):
        ui.show_div(self.pos, self.size, color=self.color, pan=pan)
        # show id
        if self.id is not None:
            if self.id_img is None:
                self.id_img = ui.get_text_img(str(self.id), font=f.tnr(25), color=(255, 255, 255))
            center = (self.pos[0] + self.size[0] // 2, self.pos[1] + self.size[1] // 2)
            ui.show_img(center, self.id_img, pan=pan, align=(1, 1))
