class Scene:
    def __init__(self, name):
        self.name = name
        self.is_active = False

    def activate(self):
        self.is_active = True
        self.on_enter()

    def deactivate(self):
        self.is_active = False
        self.on_exit()

    def on_enter(self):
        pass

    def on_exit(self):
        pass

class SceneManager:
    def __init__(self):
        self.scenes = {}
        self.active_scene = None

    def add_scene(self, scene):
        self.scenes[scene.name] = scene

    def switch_to(self, scene_name):
        if self.active_scene:
            self.active_scene.deactivate()
        self.active_scene = self.scenes.get(scene_name)
        if self.active_scene:
            self.active_scene.activate()