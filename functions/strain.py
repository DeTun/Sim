import math
import numpy as np


class Strain:
    __mOpening = True
    __mClosing = not __mOpening

    def __init__(self, f_tot, length, diameter, elasticity, timestep):
        self.__mTotalForce = f_tot
        self.__mTieBarLength = length
        self.__mTieBarArea = math.pi * 0.25 * diameter**2
        self.__mElasticity = elasticity
        self.__mTimeStep = timestep
        self.__mMaxStrain = self.__mTotalForce / (self.__mTieBarArea * 4 * self.__mElasticity) * 10**-6
        self.__mDeltaLength = self.__mTieBarLength * self.__mMaxStrain

    def __strain_force(self, duration, opening):
        strain = np.zeros(duration)
        energy_strain = np.zeros(duration)
        power_strain = np.zeros(duration)

        for i in range(duration):
            strain[i] = self.__mMaxStrain * math.sin(2 * math.pi * (.25 / duration) * i)
            energy_strain[i] = (0.5 * self.__mTieBarArea) * (4 * self.__mTieBarLength) * (
                    self.__mElasticity * 10**9) * strain[i]**2
            power_strain[i] = (energy_strain[i] - energy_strain[i-1]) / self.__mTimeStep
        if opening:
            strain = strain[::-1]
            energy_strain = energy_strain[::-1]
            power_strain = power_strain[::-1]

        return strain, energy_strain, power_strain

    def strain_during_lock(self, duration: int) -> list[float, float, float]:
        return self.__strain_force(duration, self.__mClosing)

    def strain_during_unlock(self, duration: int) -> list[float, float, float]:
        return self.__strain_force(duration, self.__mOpening)
