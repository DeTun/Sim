import numpy as np

# Function looks both ways to determine current value 
def moving_average(data: list[float], moving_points: int, total_loops: int = 1) -> list[float]:
    for i in range(total_loops):
        ma = int(moving_points / 2)
        for j in range(len(data)):
            if j >= ma and j + ma < len(data):
                sum = data[j]
                for k in range(1, ma + 1):
                    sum += data[j+k] # future
                    sum += data[j-k] # past
                data[j] = sum / ((ma * 2) + 1)
    return data

# Funcion looks into the future to determine current value
def moving_average_future_based(data: list[float], moving_points: int, total_loops: int = 1) -> list[float]:
    for i in range(total_loops):
        for j in range(len(data)):
            if j + moving_points < len(data):
                data[j] = np.sum(data[j:j+moving_points+1]) / moving_points
    return data

# Functions looks into the history of datapoints to determine current value
def moving_average_history_based(data: list[float], moving_points: int, total_loops: int = 1) -> list[float]:
    for i in range(total_loops):
        for j in range(len(data)):
            if j > moving_points:
                data[j] = np.sum(data[j-moving_points+1:j+1]) / moving_points
    return data
