class F6:
    def __init__(self):
        self.__maxVelocity = None
        self.__pid = None


    def set_max_velocity(self, velocity: float) -> None:
        self.__maxVelocity = velocity