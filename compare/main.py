# This is a sample Python script.
import threading
import matplotlib.pyplot as plt
import math
import csv
import datetime
import concurrent.futures
from solve_tsp import *
from tqdm import tqdm


def compare_algo(num_of_nodes):
    cities = cp.random.rand(num_of_nodes, 2)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        tour1_future = executor.submit(farthest_insertion, cities)
        tour2_future = executor.submit(tsp_dp, cities)
        tour1 = tour1_future.result()
        tour2 = tour2_future.result()
    fih_distance = calculate_tour_distance(tour1, cities)
    dp_distance = calculate_tour_distance(tour2, cities)
    return math.isclose(fih_distance, dp_distance, rel_tol=1e-10)


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


# Create a lock
lock = threading.Lock()


def log_to_csv(results, filename="result-{}.csv".format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))):
    with lock:
        with open(filename, "a", newline='') as file:
            writer = csv.writer(file)
            writer.writerows(results)


def compare_and_log(num_of_nodes, j):
    res = compare_algo(num_of_nodes)
    return (num_of_nodes, res)


def log_and_compare(num_of_nodes):
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(compare_and_log, num_of_nodes, j) for j in range(eachGroup)]
        for future in tqdm(concurrent.futures.as_completed(futures), total=eachGroup, desc="Progress"):
            results.append(future.result())
    try:
        log_to_csv(results, '../../TSP-FIH/mainRes.csv')
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Alternative location saved due to error")
        log_to_csv(results)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    eachGroup = 50
    startingGroup = 16
    endingGroup = 20
    for num_of_nodes in range(startingGroup, endingGroup + 1):
        print("Testing group {}.".format(num_of_nodes))
        log_and_compare(num_of_nodes)
