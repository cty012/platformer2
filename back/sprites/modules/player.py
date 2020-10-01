import utils.fonts as f
import utils.functions as utils


class Player:
    def __init__(self, player_info, id=None, squeezable=True):
        # basic info
        self.id = id
        self.id_img = None
        self.pos = player_info['pos'][:]
        self.size = player_info['size'][:]
        self.color = player_info['color'][:]
        self.squeezable = squeezable
        self.compressed_size = 0
        # movement
        self.speed = [0, 0]
        self.gravity = [0, 2]
        # status
        self.reference_frame = None
        self.ground = False
        self.jump_times = 0

    def create_rect(self, pos1, pos2):
        return [
            [min(pos1[0], pos2[0]), min(pos1[1], pos2[1])],
            [max(pos1[0], pos2[0]) + self.size[0], max(pos1[1], pos2[1]) + self.size[1]]
        ]

    def get_rect(self):
        return self.create_rect(self.pos, self.pos)

    def get_moving_rect(self, target_pos):
        return self.create_rect(self.pos, target_pos)

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
        for obs in map.objects['elevator'] + map.objects['obstacle']:
            obs_rect = obs.get_rect()
            obs_orig_rect = obs.get_orig_rect()
            if utils.overlap(self.get_moving_rect(pos), obs_rect):
                rel_pos = utils.direction(self.get_rect(), obs_orig_rect, direction)
                # return to the edge
                if rel_pos == 'low' and magnitude >= obs.speed[direction]:
                    pos[direction] = obs_rect[0][direction] - self.size[direction]
                    self.speed[direction] = obs.speed[direction]
                    # detect if player is on the ground
                    if direction == 1:
                        self.reference_frame = obs
                        self.ground = True
                        self.jump_times = 1
                elif rel_pos == 'high' and magnitude <= obs.speed[direction]:
                    pos[direction] = obs_rect[1][direction]
                    self.speed[direction] = obs.speed[direction]
        return pos

    def check_squeeze(self, map):
        # extend by 4
        orig_pos, orig_size = self.pos[:], self.size[:]
        self.compressed_size = self.squeeze(
            self.pos, self.size, self.compressed_size, -4 if self.compressed_size > 4 else -self.compressed_size, 'high'
        )
        # squeeze
        for obs in map.objects['obstacle'] + map.objects['elevator']:
            if not utils.overlap(self.get_rect(), obs.get_rect()):
                continue
            orig_rect = [orig_pos, [orig_pos[0] + self.size[0], orig_pos[1] + self.size[1]]]
            rel_pos = utils.direction(orig_rect, obs.get_orig_rect(), 1)
            diff = (self.pos[1] + self.size[1]) - obs.pos[1] if rel_pos == 'low' else (obs.pos[1] + obs.size[1]) - self.pos[1]
            self.compressed_size = self.squeeze(self.pos, self.size, self.compressed_size, diff, rel_pos)

    def squeeze(self, pos, size, compressed_size, length, direction):
        if direction != 'low':
            pos[1] += length
        size[1] -= length
        compressed_size += length
        return compressed_size

    def collide_with(self, obj):
        return utils.overlap(self.get_rect(), obj.get_rect())

    def will_collide_with(self, obj):
        pos1 = self.pos[:]
        pos1[0] += self.speed[0]
        pos2 = pos1[:]
        pos2[1] += self.speed[1]
        return utils.overlap(self.get_moving_rect(pos1), obj.get_rect()) or \
               utils.overlap(self.create_rect(pos1, pos2), obj.get_rect())

    def move(self, map):
        # move horizontally
        self.pos = self.check_obstacles(map, self.speed[0], 0)
        # move vertically
        self.pos = self.check_obstacles(map, self.speed[1], 1)
        # squeeze
        if self.squeezable:
            self.check_squeeze(map)
        # update speed
        self.speed[1] += self.gravity[1]

    def get_status(self):
        return {'pos': self.pos, 'size': self.size}

    def set_status(self, status):
        self.pos = status['pos']
        self.size = status['size']

    def show(self, ui, *, pan=(0, 0)):
        ui.show_div(self.pos, self.size, color=self.color, pan=pan)
        # show id
        if self.id is not None:
            if self.id_img is None:
                self.id_img = ui.get_text_img(str(self.id), font=f.tnr(25), color=(255, 255, 255))
            center = (self.pos[0] + self.size[0] // 2, self.pos[1] + self.size[1] // 2)
            ui.show_img(center, self.id_img, pan=pan, align=(1, 1))
