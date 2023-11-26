import concurrent.futures
import math

from solve_tsp import *
from tqdm import tqdm


def run_compare(num_of_nodes):
    cities = cp.random.rand(num_of_nodes, 2)
    tour1 = farthest_insertion(cities)
    tour2 = tsp_dp(cities)
    fih_distance = calculate_tour_distance(tour1, cities)
    dp_distance = calculate_tour_distance(tour2, cities)
    return math.isclose(fih_distance, dp_distance, rel_tol=1e-10)


if __name__ == '__main__':
    # Press the green button in the gutter to run the script.
    eachGroup = 50
    startingGroup = 10
    endingGroup = 11

    # Create a list of tasks
    tasks = [(i, eachGroup) for i in range(startingGroup, endingGroup + 1)]

    # Create a progress bar
    pbar = tqdm(total=len(tasks)*eachGroup)

    # Define a callback function to update the progress bar
    def update(*a):
        pbar.update()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Use map function to run the tasks in parallel and automatically handle results as they become available
        for task in tasks:
            for _ in range(eachGroup):
                executor.submit(run_compare, task[0]).add_done_callback(update)

    pbar.close()