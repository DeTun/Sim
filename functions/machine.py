class Machine:
    def __init__(self):
        # Global parameters
        self.motorInertia, self.motorGearRatio = 0, 0
        self.massCrossHead, self.massLSP, self.massMold = 0, 0, 0

        # Cycle specific input
        self.lengthStroke, self.timeStep = 0, 0

        # Closing movement parameters
        self.maxVc, self.dieKissVc = 0, 0

        # Locking, defining accelerations and time
        self.accelLock, self.accelTime = 0, 0

        # Locking, defining decelerations and time
        self.decelLock, self.decelTime = 0, 0

        self.timeStart = 0

    def set_machine_parameters(self, inertia, gear_ratio, cross_head, mass_lsp, mass_mold):
        self.motorInertia = inertia
        self.motorGearRatio = gear_ratio
        self.massCrossHead = cross_head
        self.massLSP = mass_lsp
        self.massMold = mass_mold

    def set_cycle_parameters(self, stroke_length, time_step):
        self.lengthStroke = stroke_length
        self.timeStep = time_step

    def set_closing_movement(self, max_vc, die_kiss):
        self.maxVc = max_vc
        self.dieKissVc = die_kiss

    def set_accel_lock(self, lock, time):
        self.accelLock = lock
        self.accelTime = time

    def set_decel_lock(self, lock, time):
        self.decelLock = lock
        self.decelTime = time
