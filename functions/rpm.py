import math

def RPM_from_speed(speed: list[float], gears: float) -> list[float]:
    """Return the RPM based on speed and gear diameter"""

    rpm = speed / (gears / 1000) * 60
    return rpm

def wRPM_from_RPM(rpm: list[float]) -> list[float]:
    """Return the angular velocity (rad/s) based on RPM"""

    angular_velocity = (rpm / 60) * 2 * math.pi
    return angular_velocity

def wRPM_from_speed(speed: list[float], gears: float) -> list[float]:
    """Return the angular velocity (rad/s) based on speed and gear diameter.
    Composed by combining two functions: speed + gears -> RPM -> wRPM"""

    rpm = RPM_from_speed(speed, gears)
    angular_velocity = wRPM_from_RPM(rpm)
    return angular_velocity
