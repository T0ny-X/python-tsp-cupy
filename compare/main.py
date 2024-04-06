# This is a sample Python script.
import concurrent.futures
import csv
import datetime
import math
import threading

import matplotlib.pyplot as plt
from tqdm import tqdm

from solve_tsp import *


# Compare_only functions
def compare_cost(tour1, tour2, cities):
    fih_distance = calculate_tour_distance(tour1, cities)
    dp_distance = calculate_tour_distance(tour2, cities)
    return math.isclose(fih_distance, dp_distance, rel_tol=1e-10)


def compare_path(path1, path2, cities):
    if len(path1) != len(path2):
        return 0
    if path1 == path2:
        return len(cities)
    path1_loop = path1 + [path1[0]]

    correct_segments_clock = len(cities)
    correct_segments_c_clock = len(cities)
    for i in range(len(cities)):
        segment_A = path1_loop[i]
        segment_B = path1_loop[i + 1]
        if path2.index(segment_A) + 1 != path2.index(segment_B):
            correct_segments_clock -= 1
        if path2.index(segment_B) + 1 != path2.index(segment_A):
            correct_segments_c_clock -= 1
    res = max(correct_segments_clock, correct_segments_c_clock)
    if res == len(cities) - 1:
        return len(cities)  # Due to property of inversion, only miss one is impossible in a loop
    return res


# Algorithm comparison functions
def compare_algo_cost(num_of_nodes):
    cities = cp.random.rand(num_of_nodes, 2)
    tour1 = farthest_insertion(cities)
    tour2 = tsp_dp(cities)
    return compare_cost(tour1, tour2, cities)


def compare_algo_path(num_of_nodes):
    cities = cp.random.rand(num_of_nodes, 2)
    path1 = farthest_insertion(cities)
    path2 = tsp_dp(cities)
    if not path1 or not path2:
        return 0
        # Set to store unique nodes from both paths
    print(path1)
    print(path2)
    return compare_path(path1, path2, cities)


def compare_algo_visual(num_of_nodes):
    # Generate sample city coordinates
    cities = cp.random.rand(num_of_nodes, 2)
    # Run both
    fih = farthest_insertion(cities)
    dp = tsp_dp(cities)
    # Visualize the tour
    cities = cities.get()
    visualize_tour(cities, fih, 'Farthest Insertion')
    visualize_tour(cities, dp, 'Branch and Cut')
    print("The FHI tour is:", fih)
    print("The dp is:", dp)
    print("The distance of the FHI tour is:", calculate_tour_distance(fih, cities))
    print("The distance of the optimal tour is:", calculate_tour_distance(dp, cities))


# Utility functions
def visualize_tour(cities, tour, title):
    # Convert tour to a Python list
    tour = cp.asnumpy(tour).tolist()
    # Extract x and y coordinates of cities
    x = [city[0] for city in cities]
    y = [city[1] for city in cities]

    # Plot the cities
    plt.figure()
    plt.plot(x, y, 'o', markersize=8)

    # Plot the tour
    x_tour = [x[city] for city in tour]
    y_tour = [y[city] for city in tour]
    plt.plot(x_tour, y_tour, 'x-', color='red')

    # Set labels and title
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(title)
    plt.show()


def log_to_csv(results, filename="result-{}.csv".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))):
    with lock:
        with open(filename, "a", newline='') as file:
            writer = csv.writer(file)
            writer.writerows(results)


# Main compare
def compare_algo(num_of_nodes, header=True, cost_diff=True, segment_similarity=True, visualization=False):
    cities = cp.random.rand(num_of_nodes, 2)
    tour1 = farthest_insertion(cities)
    tour2 = tsp_dp(cities)

    if segment_similarity:
        segments = compare_path(tour1, tour2, cities)
    else:
        segments = 0

    if cost_diff and segments == len(cities):
        cost = compare_cost(tour1, tour2, cities)
    else:
        cost = 0

    if visualization:
        visualize_tour(cities, tour1, 'Farthest Insertion')
        visualize_tour(cities, tour2, 'Dynamic Programming')
        if header:
            print("Number of nodes:", num_of_nodes)
        if cost_diff:
            print("Cost difference:", cost)
        if segment_similarity:
            print("Same segments:", segments)

    return [num_of_nodes, cost, segments]


# Batch Process functions
lock = threading.Lock()


def compare_and_log(num_of_nodes, j):
    res = compare_cost(num_of_nodes)
    return (num_of_nodes, res)


def log_and_compare(num_of_nodes):
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(compare_and_log, num_of_nodes, j) for j in range(eachGroup)]
        for future in tqdm(concurrent.futures.as_completed(futures), total=eachGroup, desc="Progress"):
            results.append(future.result())
    try:
        log_to_csv(results, 'mainRes.csv')
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Alternative location saved due to error")
        log_to_csv(results)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(compare_path([1, 2, 3, 4], [4, 3, 2, 1], [1, 2, 3, 4]))
    eachGroup = 10
    """
    startingGroup = 1
    endingGroup = 3
    for num_of_nodes in range(startingGroup, endingGroup + 1):
        print("Testing group {}.".format(num_of_nodes))
        log_and_compare(num_of_nodes)
    
    """
