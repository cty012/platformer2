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
        self.init_objects()
        self.descriptions = []
        if 'description' in self.map_info.keys():
            self.descriptions = self.map_info['description']

    def init_objects(self):
        MapLoader.load(self, self.map_info)

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

    def get_status(self):
        return {
            obj_type: [obj.get_status() for obj in self.objects[obj_type] if len(obj.update) > 0]
            for obj_type in ['target', 'coin', 'obstacle', 'elevator', 'monster', 'switch']
        }

    def set_status(self, status):
        for obj_type in ['target', 'coin', 'obstacle', 'elevator', 'monster', 'switch']:
            names = [obj['name'] for obj in status[obj_type]]
            i = 0
            while i < len(self.objects[obj_type]):
                obj = self.objects[obj_type][i]
                if len(obj.update) == 0:
                    i += 1
                elif 'name' in obj.update and obj.name not in names:
                    self.objects[obj_type].pop(i)
                else:
                    self.objects[obj_type][i].set_status(status[obj_type][i])
                    i += 1

    def show(self, ui, *, pan=(0, 0)):
        for desc in self.descriptions:
            for i, text in enumerate(desc['text']):
                pos = desc['pos'][0], desc['pos'][1] + i * desc['font'][1] * 2
                ui.show_text(
                    pos, text, f.get_font(desc['font'][0], desc['font'][1]),
                    color=desc['color'], pan=pan
                )
        for obj in self.get_objects():
            obj.show(ui, pan=pan)


class MapLoader:
    @classmethod
    def load(cls, map, map_info):
        for obj_name in map.objects:
            for obj_info in map_info[obj_name]:
                if obj_name in ['target', 'coin', 'obstacle']:
                    map.objects[obj_name].append(o.Static(obj_info, type=obj_name))
                elif obj_name in ['elevator', 'monster']:
                    map.objects[obj_name].append(o.Movable(obj_info, type=obj_name))
                elif obj_name == 'switch':
                    map.objects[obj_name].append(o.Switch(obj_info, type=obj_name))
