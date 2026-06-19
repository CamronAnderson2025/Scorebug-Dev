from shared.shared import *
@dataclass
class AnimationState:
    active: bool = False
    animating: bool = False
    progress: float = 0.0
    direction: int = 1
    start_time: float = 0.0
    duration: float = 1.0
class AnimationManager:
    def __init__(self):
        self.animations = {}

    def add(self, name, duration=1.0):
        self.animations[name] = AnimationState(duration=duration)

    def get(self, name):
        return self.animations[name]