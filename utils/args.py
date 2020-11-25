class Args:
    def __init__(self, scale=1, path='.', save_path='.'):
        self.scale = scale
        self.size = (1280, 720)
        self.real_size = int(self.size[0] * scale), int(self.size[1] * scale)

        self.path = path
        self.save_path = save_path
