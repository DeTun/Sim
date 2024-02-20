import numpy as np

def rotational_energy(wRPM: list[float], inertia: float) -> list[float]:
    """Return the rotation energy of the engine"""
    rot_energy = 0.5 * inertia * wRPM**2
    return rot_energy

def translational_energy(speed: list[float], mass: float) -> list[float]:
    """Return the kinetical energy (energy of motion) of the moving particle"""
    trans_energy = 0.5 * mass * speed**2
    return trans_energy

def energy_to_power(energy: list[float], delta_time: float) -> list[float]:
    """Return the power (W) based on change in energy over change in time"""
    power = np.zeros(len(energy))    
    for i in range(1, len(energy)):
        power[i] = (energy[i] - energy[i-1]) / delta_time
    return power