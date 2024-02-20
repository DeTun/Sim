import csv
import matplotlib.pyplot as plt
import numpy as np
from math import sqrt

tmp, pos_ch_measured, pos_ch_measured_doubled = [], [], []

with open('../Scoop/V1.0_S0204419.001') as file:
    data = list(csv.reader(file))

for row in data:
    pos_ch_measured.append(int(row[5]))

# minimum = np.min(pos_ch_measured) * 2
# pos_ch_measured = [i - minimum for i in pos_ch_measured]

for i in range(len(pos_ch_measured)):
    pos_ch_measured_doubled.append(pos_ch_measured[i])
    if i + 2 < len(pos_ch_measured):
#        distance_factor_2ms = pos_ch_measured[i + 1] / pos_ch_measured[i]
#        distance_factor_1ms = sqrt(distance_factor_2ms)
#        new_point = pos_ch_measured[i] * distance_factor_1ms

#        new_point = (pos_ch_measured[i] + pos_ch_measured[i + 1]) / 2

#        new_point = pos_ch_measured[i] + ((pos_ch_measured[i + 1] - pos_ch_measured[i]) * 0.50001)
        energy_1 = 3788.43682403 * (((pos_ch_measured[i + 1] / 1e6) - (pos_ch_measured[i]) / 1e6) / 0.002)**2
        energy_2 = 3788.43682403 * (((pos_ch_measured[i + 2] / 1e6) - (pos_ch_measured[i + 1]) / 1e6) / 0.002)**2

        energy_extra_point = (energy_1 + energy_2) / 2
        # energy = 3788 * velocity^2 --> energy / 3788 = velocity^2 --> velocity^2 = energy / 3788
        velocity_m_s_squared = energy_extra_point / 3788.43682403
        velocity_m_s = sqrt(velocity_m_s_squared)

        if pos_ch_measured[i] < pos_ch_measured[i-1]:
            velocity_m_s = -velocity_m_s

        velocity_nm = velocity_m_s * 1e6
        new_point = pos_ch_measured[i] + (velocity_nm * 0.001)
        pos_ch_measured_doubled.append(new_point)

pos_ch_measured_doubled.append(pos_ch_measured[len(pos_ch_measured) - 1])
pos_ch_measured_doubled.append(pos_ch_measured[len(pos_ch_measured) - 1])

# pos_ch_measured_doubled = [i + minimum for i in pos_ch_measured_doubled]
# """
moving_average = 10
temp_pos = pos_ch_measured_doubled.copy()
for j in range(len(pos_ch_measured_doubled)):
    if j > moving_average:
        pos_ch_measured_doubled[j] = (1 / moving_average) * (temp_pos[j] +
                                                             np.sum(temp_pos[(j - moving_average + 1):j]))
# """

with open('../Scoop/ch_pos_1ms.001', 'w') as file:
    for item in range(len(pos_ch_measured_doubled)):
        file.write(str(int(pos_ch_measured_doubled[item])) + "\n")

"""
V_1ms = np.zeros(len(pos_ch_measured_doubled))
for i in range(len(pos_ch_measured_doubled) - 1):
    V_1ms[i] = (pos_ch_measured_doubled[i + 1] - pos_ch_measured_doubled[i]) / 0.001

V_2ms = np.zeros(len(pos_ch_measured))
for i in range(len(pos_ch_measured) - 1):
    V_2ms[i] = (pos_ch_measured[i + 1] - pos_ch_measured[i]) / 0.002

fig1, ax1 = plt.subplots()
ax1.plot(pos_ch_measured, color='r')
ax2 = ax1.twiny()
ax2.plot(pos_ch_measured_doubled, color='b')

fig2, ax3 = plt.subplots()
ax3.plot(V_1ms, color='r')
ax4 = ax3.twiny()
ax4.plot(V_2ms, color='b')


plt.show()
"""
