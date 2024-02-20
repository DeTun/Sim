import csv
import math
import numpy as np
import matplotlib.pyplot as plt

from functions import lsp
from functions import moving_average
from functions import strain

lsp = lsp.LSP()
lsp.set_length(255.0, 169.7, 85.0, 260.0, 175.0, 500.0, 535.0, 440.0)
strain = strain.Strain(4400, 3.987, 0.115, 210, 0.002)

delay = 0.01
timing = 0.002

shift = int(delay/timing)

with open('../Scoop/V1.1_S0204419.001') as file:
    data = list(csv.reader(file))

pos_ch_setpoint = np.zeros(len(data))
velo_ch_setpoint = np.zeros(len(data))
acc_ch_setpoint = np.zeros(len(data))

pos_ch_measured = np.zeros(len(data))
velo_ch_measured = np.zeros(len(data))

pos_ch_calculated = np.zeros(len(data))
velo_ch_calculated = np.zeros(len(data))

percentile_power = np.zeros(len(data))

# Append data to lists
i = 0
for row in data:
    velo_ch_setpoint[i] = float(row[0]) / 1e6
    pos_ch_measured[i] = float(row[5]) / 1e6
    percentile_power[i] = float(row[6]) / -1e5
    i += 1

# Duplicating list so possible to see original input and calculated outcome.
velo_ch_calculated = velo_ch_setpoint

# Depending on the given delay, rotate the list --> move backwards --> add delay
velo_ch_calculated = np.roll(velo_ch_calculated, shift)

# Assigning same starting position, else it will default to zero
pos_ch_setpoint[0] = pos_ch_calculated[0] = pos_ch_measured[0]
for i in range(1, len(velo_ch_setpoint)):
    pos_ch_setpoint[i] = pos_ch_setpoint[i-1] + (velo_ch_setpoint[i] * 0.002)
    acc_ch_setpoint[i] = (velo_ch_setpoint[i] - velo_ch_setpoint[i-1]) / 0.002

for i in range(len(pos_ch_measured)):
    velo_ch_measured[i] = (pos_ch_measured[i] - pos_ch_measured[i-1]) / 0.002

# Starting the manipulation of input signal 
start_index_strain, end_index_strain = 0, 0
for i in range(len(pos_ch_setpoint)):
    if pos_ch_setpoint[i] > 0.0001 > pos_ch_setpoint[i - 1]:
        start_index_strain = i + shift
        break

for i in range(len(acc_ch_setpoint)):
    if acc_ch_setpoint[i] == 0 > acc_ch_setpoint[i - 1]:
        end_index_strain = i + shift
        break
size = end_index_strain - start_index_strain
n_strain, e_strain, p_strain = strain.strain_during_unlock(size)

w_rpm_calculated = np.zeros(size)
rot_energy_calculated = np.zeros(size)
kin_energy_calculated = np.zeros(size)

for i in range(size):
    w_rpm_calculated[i] = (velo_ch_setpoint[i + start_index_strain + shift] / (20.92 / 1000)) * 2 * math.pi
    rot_energy_calculated[i] = 0.5 * 0.084 * w_rpm_calculated[i]**2

    calculated_prev_lsp = lsp.pos_lsp(pos_ch_setpoint[i - 1 + start_index_strain + shift] * -1000) / 1000
    calculated_curr_lsp = lsp.pos_lsp(pos_ch_setpoint[i + start_index_strain + shift] * -1000) / 1000
    calculated_velo_lsp = (calculated_curr_lsp - calculated_prev_lsp) / 0.002
    kin_energy_calculated[i] = (137.5 * velo_ch_calculated[i]**2) + (2030.5 * calculated_velo_lsp**2)

total_energy_calculated = rot_energy_calculated + kin_energy_calculated

for i in range(1, size):
    percentile_energy_rotation = rot_energy_calculated[i] / total_energy_calculated[i]
#    delta_e_strain = abs(e_strain[i] - e_strain[i-1]) * percentile_energy_rotation * 0.12  # Best approx. peak speed
    delta_e_strain = abs(e_strain[i] - e_strain[i-1]) * percentile_energy_rotation * 0.25  # Same efficiency
#    delta_e_strain = abs(e_strain[i] - e_strain[i-1]) * percentile_energy_rotation * 0.35  # Perfect match CRH @85mm
    additional_velo = math.sqrt(delta_e_strain / 3788.43682403)
    velo_ch_calculated[start_index_strain + i] += additional_velo

closing_delay = 0.006
closing_shift = int(closing_delay / timing)

for i in range(closing_shift):
    velo_ch_calculated = np.delete(velo_ch_calculated, -1)
    velo_ch_calculated = np.insert(velo_ch_calculated, 1000, velo_ch_calculated[999])

top_speed_m_s = 0.9
j, k = 1, 1
for i in range(len(velo_ch_calculated)):
    if velo_ch_calculated[i] >= top_speed_m_s * 0.75 and velo_ch_calculated[i] > velo_ch_calculated[i-1]:
        velo_ch_calculated[i] -= (velo_ch_calculated[i] - velo_ch_calculated[i-1]) * 0.9 * ((j/10)**2)
        if j < 10:
            j += 1
    elif velo_ch_calculated[i] <= -top_speed_m_s * 0.65 and velo_ch_calculated[i] < velo_ch_calculated[i-1]:
        velo_ch_calculated[i] -= (velo_ch_calculated[i] - velo_ch_calculated[i-1]) * 0.9 * ((k/10)**2)
        if k < 10:
            k += 1

for i in range(1, len(velo_ch_calculated)):
    pos_ch_calculated[i] = pos_ch_calculated[i-1] + (velo_ch_calculated[i] * 0.002)

# Ending index is currently hardcoded, no idea how to determine it right now based on input
start_index_strain, end_index_strain = 0, 1674
for i in range(len(pos_ch_calculated)):
    if pos_ch_calculated[i] < 0.075 < pos_ch_calculated[i - 1]:
        start_index_strain = i
        break

size = end_index_strain - start_index_strain
n_strain, e_strain, p_strain = strain.strain_during_lock(size)

w_rpm_calculated = np.zeros(size)
rot_energy_calculated = np.zeros(size)
kin_energy_calculated = np.zeros(size)

for i in range(size):
    w_rpm_calculated[i] = (velo_ch_calculated[i + start_index_strain] / (20.92 / 1000)) * 2 * math.pi
    rot_energy_calculated[i] = 0.5 * 0.084 * w_rpm_calculated[i]**2

    calculated_prev_lsp = lsp.pos_lsp(pos_ch_calculated[i - 1 + start_index_strain] * -1000) / 1000
    calculated_curr_lsp = lsp.pos_lsp(pos_ch_calculated[i + start_index_strain] * -1000) / 1000
    calculated_velo_lsp = (calculated_curr_lsp - calculated_prev_lsp) / 0.002
    kin_energy_calculated[i] = (137.5 * velo_ch_calculated[i]**2) + (2030.5 * calculated_velo_lsp**2)

total_energy_calculated = rot_energy_calculated + kin_energy_calculated

for i in range(1, size):
    print(round(rot_energy_calculated[i], 4))

for i in range(1, size):
    percentile_energy_rotation = rot_energy_calculated[i] / total_energy_calculated[i]
#    delta_e_strain = abs(e_strain[i] - e_strain[i-1]) * percentile_energy_rotation * 0.12  # Best approx. peak speed
    delta_e_strain = abs(e_strain[i] - e_strain[i-1]) * percentile_energy_rotation * 0.10  # Same efficiency
#    delta_e_strain = abs(e_strain[i] - e_strain[i-1]) * percentile_energy_rotation * 0.35  # Perfect match CRH @85mm
    additional_velo = math.sqrt(delta_e_strain / 3788.43682403)
    velo_ch_calculated[start_index_strain + i] -= additional_velo

for i in range(1, len(velo_ch_calculated)):
    pos_ch_calculated[i] = pos_ch_calculated[i-1] + (velo_ch_calculated[i] * 0.002)

# Both setpoint as actual measured have a velocity element
# First calculate the RMP of each
rpm_setpoint = np.zeros(len(pos_ch_setpoint))
rpm_measured = np.zeros(len(pos_ch_measured))
for i in range(len(rpm_setpoint)):
    rpm_setpoint[i] = velo_ch_setpoint[i] / (20.92 / 1000) * 60
    rpm_measured[i] = velo_ch_measured[i] / (20.92 / 1000) * 60

# Then calculate the angular RPM (wRPM) of each
w_rpm_setpoint = np.zeros(len(rpm_setpoint))
w_rpm_measured = np.zeros(len(rpm_measured))
for i in range(len(w_rpm_setpoint)):
    w_rpm_setpoint[i] = (rpm_setpoint[i] / 60) * 2 * math.pi
    w_rpm_measured[i] = (rpm_measured[i] / 60) * 2 * math.pi

# Both setpoint as actual measured have an angular (wRPM) element
# Secondly, calculate the rotational energy of both
rot_energy_setpoint = np.zeros(len(pos_ch_setpoint))
rot_energy_measured = np.zeros(len(pos_ch_measured))
for i in range(len(rot_energy_setpoint)):
    rot_energy_setpoint[i] = 0.5 * 0.084 * (w_rpm_setpoint[i]**2)
    rot_energy_measured[i] = 0.5 * 0.084 * (w_rpm_measured[i]**2)

# Both setpoint as actual measured have an angular (wRPM) element
# Thirdly, calculate the kinetic energy of both
kin_energy_setpoint = np.zeros(len(pos_ch_setpoint))
kin_energy_measured = np.zeros(len(pos_ch_measured))
for i in range(1, len(kin_energy_setpoint)):
       setpoint_prev_lsp = lsp.pos_lsp(pos_ch_setpoint[i-1] * -1000) / 1000
       setpoint_curr_lsp = lsp.pos_lsp(pos_ch_setpoint[i] * -1000) / 1000
       setpoint_velo_lsp = (setpoint_curr_lsp - setpoint_prev_lsp) / 0.002
       kin_energy_setpoint[i] = (137.5 * velo_ch_setpoint[i]**2) + (2030.5 * setpoint_velo_lsp**2)

       measured_prev_lsp = lsp.pos_lsp(pos_ch_measured[i-1] * -1000) / 1000
       measured_curr_lsp = lsp.pos_lsp(pos_ch_measured[i] * -1000) / 1000
       measured_velo_lsp = (measured_curr_lsp - measured_prev_lsp) / 0.002
       kin_energy_measured[i] = (137.5 * velo_ch_measured[i]**2) + (2030.5 * measured_velo_lsp**2)

total_energy_setpoint = rot_energy_setpoint + kin_energy_setpoint
total_energy_measured = rot_energy_measured + kin_energy_measured

total_power_setpoint = np.zeros(len(total_energy_setpoint))
total_power_measured = np.zeros(len(total_energy_measured))
for i in range(len(total_power_setpoint)):
    total_power_setpoint[i] = (total_energy_setpoint[i] - total_energy_setpoint[i-1]) / 0.002
    total_power_measured[i] = (total_energy_measured[i] - total_energy_measured[i-1]) / 0.002

torque_setpoint = np.zeros(len(total_power_setpoint))
torque_measured = np.zeros(len(total_power_measured))
for i in range(len(torque_setpoint)):
    if w_rpm_setpoint[i] != 0:
        torque_setpoint[i] = total_power_setpoint[i] / w_rpm_setpoint[i]
        if torque_setpoint[i] > 500 or torque_setpoint[i] < -500:
            torque_setpoint[i] = 1
    if w_rpm_measured[i] != 0:
        torque_measured[i] = total_power_measured[i] / w_rpm_measured[i]
"""
iterations = 3
for j in range(iterations):
    ma = 4
    for i in range(len(torque_measured)):
        if i > ma:
            torque_measured[i] = (1/ma) * np.sum(torque_measured[i-ma+1:i+1])
"""

# pos_ch_setpoint = [(i - 6341) / 1e3 for i in pos_ch_setpoint]
# pos_ch_measured = [i / 1e3 for i in pos_ch_measured]

nominal_Nm = 330

open_Nm = np.zeros(len(percentile_power))
for i in range(len(percentile_power)):
    open_Nm[i] = nominal_Nm * percentile_power[i]


figure1, axis1 = plt.subplots()
axis1.set_xlabel("Time [2ms per measure]")
axis1.set_ylabel("Torque [kN]")
axis1.plot(torque_measured, color='tab:blue', label="measured")
axis1.plot(torque_setpoint, color='tab:orange', label="setpoint")
axis1.legend(loc=0)

figure2, axis2 = plt.subplots()
axis2.set_xlabel("Time [2ms per measure]")
axis2.set_ylabel("Power [kWh]")
axis2.plot(total_power_measured/1000, color='tab:blue', label="measured")
axis2.plot(total_power_setpoint/1000, color='tab:orange', label="setpoint")
axis2.legend(loc=0)

figure3, axis3 = plt.subplots()
axis3.set_xlabel("Time [2ms per measure]")
axis3.set_ylabel("Rotation [wRPM]")
axis3.plot(w_rpm_measured, color='tab:blue', label="measured")
axis3.plot(w_rpm_setpoint, color='tab:orange', label="setpoint")
axis3.legend(loc=0)

plt.show()

"""
fig, ax = plt.subplots()
ax.set_xlabel("Time [2ms per measure]")
ax.set_ylabel("CRH speed [mm/s]")
ax.plot(velo_ch_calculated, color='tab:green', label="Calculated")
ax.plot(velo_ch_setpoint, color='tab:blue', label="Setpoint")
ax.plot(velo_ch_measured, color='tab:orange', label="Measured")

ax.tick_params(axis='x')
ax.legend(loc=0)

for i in range(len(pos_ch_setpoint)):
    if pos_ch_setpoint[i] > 0.0001 > pos_ch_setpoint[i - 1] or pos_ch_setpoint[i] < 0.0001 < pos_ch_setpoint[i - 1]:
        plt.axvline(x=i, color='tab:blue', alpha=.3)
    if pos_ch_setpoint[i] > 0.0787 > pos_ch_setpoint[i - 1] or pos_ch_setpoint[i] < 0.075 < pos_ch_setpoint[i - 1]:
        plt.axvline(x=i, color='tab:blue', alpha=.3)

for i in range(len(pos_ch_measured)):
    if pos_ch_measured[i] > 0.0001 > pos_ch_measured[i - 1] or pos_ch_measured[i] < 0.0001 < pos_ch_measured[i - 1]:
        plt.axvline(x=i, color='tab:orange', alpha=.6)
    if pos_ch_measured[i] > 0.0787 > pos_ch_measured[i - 1] or pos_ch_measured[i] < 0.075 < pos_ch_measured[i - 1]:
        plt.axvline(x=i, color='tab:orange', alpha=.6)

for i in range(len(pos_ch_calculated)):
    if pos_ch_calculated[i] > 0.0001 > pos_ch_calculated[i - 1] or \
            pos_ch_calculated[i] < 0.0001 < pos_ch_calculated[i - 1]:
        plt.axvline(x=i, color='tab:green', alpha=.6)
    if pos_ch_calculated[i] > 0.0787 > pos_ch_calculated[i - 1] or \
            pos_ch_calculated[i] < 0.075 < pos_ch_calculated[i - 1]:
        plt.axvline(x=i, color='tab:green', alpha=.6)


plt.axvline(x=1000, color='k')

ax1 = ax.twinx()
ax1.set_ylabel("CRH position [mm]")
ax1.plot(pos_ch_calculated, color='tab:green', label="Calculated")
ax1.plot(pos_ch_setpoint, color='tab:blue', label="Setpoint")
ax1.plot(pos_ch_measured, color='tab:orange', label="Measured")

# ax2 = ax.twinx()
# ax2.plot(acc_ch_setpoint, color='g')

fig2, ax3 = plt.subplots()
ax3.plot(torque_measured, label="Measured")
ax3.plot(torque_setpoint, label="Setpoint")
ax3.plot(open_Nm, label="Open Nm")
ax3.legend(loc=0)

plt.show()
"""