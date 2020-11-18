import back.sprites.modules.object as o
import utils.fonts as f
import utils.functions as utils


class Map:
    def __init__(self, mode, map_info, pos, *, align=(0, 0)):
        self.mode = mode
        self.map_info = map_info
        self.size = self.map_info['size']
        self.pos = utils.top_left(pos, self.size, align=align)
        # objects
        self.objects = {
            'target': [],
            'obstacle': [],
            'elevator': [],
            'switch': [],
            'coin': [],
            'monster': [],
        }
        self.updatable = []
        self.init_objects()
        self.descriptions = []
        if 'description' in self.map_info.keys():
            self.descriptions = self.map_info['description']

    def init_objects(self):
        MapLoader.load(self, self.map_info)

    def get_rect(self):
        return [self.pos, [self.pos[0] + self.size[0], self.pos[1] + self.size[1]]]

    def in_range(self, pos):
        return self.pos[0] < pos[0] < self.pos[0] + self.size[0] and \
               self.pos[1] < pos[1] < self.pos[1] + self.size[1]

    def get_objects(self):
        objs = []
        for obj_name in self.objects.keys():
            objs += self.objects[obj_name]
        return objs

    def find_objects(self, name):
        results = []
        for obj in self.get_objects():
            if obj.name == name:
                results.append(obj)
        return results

    def remove_objects(self, name):
        for obj in self.find_objects(name):
            self.objects[obj.type].remove(obj)
        i = 0
        while i < len(self.updatable):
            if self.updatable[i].name == name:
                self.updatable.pop(i)
            else:
                i += 1

    def get_status(self):
        return [obj.get_status() for obj in self.updatable if len(obj.update) > 0]

    def set_status(self, status):
        names = [obj_status['name'] for obj_status in status if 'name' in obj_status.keys()]
        i = 0
        while i < len(self.updatable):
            obj = self.updatable[i]
            if 'name' in obj.update and obj.name not in names:
                self.remove_objects(obj.name)
            else:
                obj.set_status(status[i])
                i += 1

    def show(self, ui, *, pan=(0, 0)):
        for desc in self.descriptions:
            for i, text in enumerate(desc['text']):
                pos = desc['pos'][0], desc['pos'][1] + i * desc['font'][1] * 2
                ui.show_text(
                    pos, text, f.get_font(desc['font'][0], desc['font'][1]),
                    color=desc['color'], save=str(desc['font']) + '-' + str(desc['color']), pan=pan
                )
        for obj in self.get_objects():
            if not utils.overlap(self.get_rect(), obj.get_rect(pan=pan)):
                continue
            obj.show(ui, pan=pan)


class MapLoader:
    @classmethod
    def load(cls, map, map_info):
        for obj_name in map.objects:
            for obj_info in map_info[obj_name]:
                # create object
                if obj_name in ['target', 'coin', 'obstacle']:
                    obj = o.Static(obj_info, type=obj_name)
                elif obj_name in ['elevator', 'monster']:
                    obj = o.Movable(obj_info, type=obj_name)
                elif obj_name == 'switch':
                    obj = o.Switch(obj_info, type=obj_name)
                else:
                    obj = None
                # append to lists
                map.objects[obj_name].append(obj)
                if 'update' in obj_info.keys():
                    map.updatable.append(obj)
