import csv
import math
import numpy as np
import matplotlib.pyplot as plt

from functions import energy
from functions import lsp
from functions import rpm
from functions import strain
from functions import moving_average

def read_file(file_name: str, delim: str) -> tuple[list[float], list[float], list[float], float]:
    """Reads the input file, checks if the correct sensor data is available. Returns lists of data"""
    velocity_setpoint = '/clp/o/VY'
    position_measured = '/clp/i/PO'
    pressure_measured = '/clp/i/PR'
    seconds_per_cycle = 4

    with open(file_name) as file:
        data = list(csv.reader(file, delimiter=delim))
    file.close()

    crh_velo = np.zeros(len(data))
    crh_posi = np.zeros(len(data))
    crh_torq  = np.zeros(len(data))
    x = y = z = timing = -1

    for i in range(len(data)):
        if -1 in {x, y, z} and len(data[i]) == 1:
            if data[i][0] == velocity_setpoint: x = i
            if data[i][0] == position_measured: y = i
            if data[i][0] == pressure_measured: z = i
        elif len(data[i]) > 1 and -1 in {x, y, z}:
            raise ValueError("The required sensor is not in the scoop")
        elif len(data[i]) > 1 and -1 in {timing}:
            timing = i
        elif data[i][0] == "SCOOPTRIGGER":
            timing = seconds_per_cycle / (i - timing)
            break
        else:
            crh_velo[i] = float(data[i][x]) / 1e3
            crh_posi[i] = float(data[i][y]) / 1e3
            crh_torq[i] = float(data[i][z])

    return crh_velo, crh_posi, crh_torq, timing

def main():
    velo, posi, torq, timing = read_file('../Scoop/V0.1_S0204419.001', ' ')
    setpoint_crh_velocity = velo
    measured_crh_position = posi
    measured_torque = [-0.008 * 0.61 * x for x in torq]

    measured_crh_velocity = np.zeros(len(measured_crh_position))
    for i in range(1, len(measured_crh_velocity)):
        measured_crh_velocity[i] = (measured_crh_position[i] 
                                    - measured_crh_position[i-1]) / timing

    setpoint_crh_position = np.zeros(len(setpoint_crh_velocity))
    for i in range(1, len(setpoint_crh_velocity)):
        setpoint_crh_position[i] = (setpoint_crh_position[i-1] 
                                    + (setpoint_crh_velocity[i] * timing))

    # Getting the angular velocity (aka wRPM)
    measured_wRPM = rpm.wRPM_from_speed(measured_crh_velocity, 20.92)
    setpoint_wRPM = rpm.wRPM_from_speed(setpoint_crh_velocity, 20.92)

    # "In physics, the kinetic energy of an object is the form of energy that
    # it possesses due to it's motion"
    # Source: https://en.wikipedia.org/wiki/Kinetic_energy

    # Since the CRH is powered by an (electric) engine it will be convenient to
    # split the total kinetic energy of the body into the sum of translational
    # kinetic energy ('linear' motion) and angular kinetic energy ('rotational'
    # motion) --> KE = E_t + E_r
    # Source: https://en.wikipedia.org/wiki/Kinetic_energy#Rotation_in_systems


    # Calculating the rotational energy / angular kinetic energy
    m_angular_kinetic_energy = energy.rotational_energy(measured_wRPM, 0.084)
    s_angular_kinetic_energy = energy.rotational_energy(setpoint_wRPM, 0.084)

    # The translational kinetic energy will be split up in two parts, this is
    # due to two independently moving objects: the crosshead (CRH) and LSP. The
    # LSP motion is directly determined by the CRH motion. However, the ratio
    # will be fluctuating and needs to be determined on every point.

    # First calculate the known translational kinetic energy: the CHR motion
    m_translational_kinetic_energy = energy.translational_energy(measured_crh_velocity, 275.0)
    s_translational_kinetic_energy = energy.translational_energy(setpoint_crh_velocity, 275.0)

    # Before we can calculate the translational kinetic energy for the LSP
    # motion, we'll need to know own velocity. Based on CRH positions, the LSP
    # positions can be determined. Then differentiate over those positions to
    # determine it's velocity.
    measured_lsp_position = np.zeros(len(measured_crh_position))
    measured_lsp_velocity = np.zeros(len(measured_crh_position))

    setpoint_lsp_position = np.zeros(len(setpoint_crh_position))
    setpoint_lsp_velocity = np.zeros(len(setpoint_crh_position))

    # Setting first element so loop can start at i=1 (for d/dx)
    measured_lsp_position[0] = lsp.pos_lsp(-measured_crh_position[0])
    setpoint_lsp_position[0] = lsp.pos_lsp(-setpoint_crh_position[0])
    for i in range(1, len(measured_lsp_position)):
        measured_lsp_position[i] = lsp.pos_lsp(-measured_crh_position[i])
        measured_lsp_velocity[i] = (measured_lsp_position[i] 
                                    - measured_lsp_position[i-1]) / timing
    
        setpoint_lsp_position[i] = lsp.pos_lsp(-setpoint_crh_position[i])
        setpoint_lsp_velocity[i] = (setpoint_lsp_position[i] 
                                    - setpoint_lsp_position[i-1]) / timing


    m_translational_kinetic_energy += energy.translational_energy(measured_lsp_velocity, 4061.0)
    s_translational_kinetic_energy += energy.translational_energy(setpoint_lsp_velocity, 4061.0)

    m_total_kinetic_energy = m_angular_kinetic_energy + m_translational_kinetic_energy
    s_total_kinetic_energy = s_angular_kinetic_energy + s_translational_kinetic_energy

    # "In physics, power is the amount of energy transferred per unit time. In
    # the SI Units, the unit of power is the watt, equal to one joule per second"
    # Power is the rate with respect to time at which work is done; it is the 
    # time derivative of work: P = dW/dt
    # Source: https://en.wikipedia.org/wiki/Power_(physics)
    m_total_power = energy.energy_to_power(m_total_kinetic_energy, timing)
    s_total_power = energy.energy_to_power(s_total_kinetic_energy, timing)
    
    # Good and understandable comments will be written next week or when I feel
    # like doing it. For now, here is just the source.
    # Source: https://en.wikipedia.org/wiki/Torque
    m_torque = np.divide(m_total_power, measured_wRPM, 
                        out=np.zeros_like(m_total_power), where=measured_wRPM!=0)
    s_torque = np.divide(s_total_power, setpoint_wRPM, 
                        out=np.zeros_like(s_total_power), where=setpoint_wRPM!=0)

    m_torque[0:150] = m_torque[len(m_torque)-150:len(m_torque)]= 0
    
    m_torque = moving_average.moving_average(m_torque, 10)
    s_torque = moving_average.moving_average(s_torque, 10)


    
    fig, ax = plt.subplots()
    ax.set_xlabel("Time [2ms per measure]")
    ax.set_ylabel("Torque [N/m]")
    ax.plot(measured_torque, color='tab:blue', label='Measured (F6)')
    ax.plot(m_torque/1e3, color='tab:orange', label='Calculated (POS -> F6)')
    ax.plot(s_torque/1e3, color='tab:green', label='Calculated (SETPOINT)')
    ax.legend(loc=0)

    plt.show()

if __name__ == "__main__":
    lsp = lsp.LSP()
    # lsp.set_length(255.0, 169.7, 85.0, 260.0, 175.0, 500.0, 535.0, 440.0)
    lsp.set_length(380.0, 171.8, 90.0, 365.0, 235.0, 605.0, 700.0, 495.0)
    strain = strain.Strain(4400, 3.987, 0.115, 210, 0.002)
    main()
