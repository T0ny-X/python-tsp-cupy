from functools import lru_cache
from typing import Dict, List, Optional, Tuple
import cupy as cp
from scipy.spatial import ConvexHull


def calculate_distance(city1, city2):
    return cp.linalg.norm(city2 - city1)


def calculate_tour_distance(tour, cities):
    # Calculate the total distance of a tour
    return sum(calculate_distance(cities[tour[i - 1]], cities[tour[i]]) for i in range(len(tour)))


def farthest_insertion(cities):
    cities = cities.get()
    hull = ConvexHull(cities)
    hull_points = cities[hull.vertices]
    max_distance = -1
    city1, city2 = None, None
    for i in range(len(hull_points)):
        for j in range(i + 1, len(hull_points)):
            distance = calculate_distance(hull_points[i], hull_points[j])
            if distance > max_distance:
                max_distance = distance
                city1, city2 = hull.vertices[i], hull.vertices[j]

    tour = [city1, city2]
    remaining_cities = set(range(len(cities))) - set(tour)
    while remaining_cities:
        min_increase = float('inf')
        city_to_insert = None
        index_to_insert = None
        for city in remaining_cities:
            for i in range(len(tour)):
                next_city = tour[(i + 1) % len(tour)]
                increase = calculate_distance(cities[city], cities[tour[i]]) + calculate_distance(cities[city], cities[
                    next_city]) - calculate_distance(cities[tour[i]], cities[next_city])
                if increase < min_increase:
                    min_increase = increase
                    city_to_insert = city
                    index_to_insert = i + 1
        tour.insert(index_to_insert, city_to_insert)
        remaining_cities.remove(city_to_insert)

    return tour


def calculate_distance_matrix(cities):
    # Calculate the distance matrix for the cities
    n = len(cities)
    distance_matrix = cp.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            distance_matrix[i, j] = distance_matrix[j, i] = calculate_distance(cities[i], cities[j])
    return distance_matrix


def tsp_dp(cities):
    # Convert cities to a distance matrix
    distance_matrix = calculate_distance_matrix(cities)

    # Solve the TSP
    permutation, _ = solve_tsp_dynamic_programming(distance_matrix)

    return permutation


def solve_tsp_dynamic_programming(
    distance_matrix: cp.ndarray,
    maxsize: Optional[int] = None,
) -> Tuple[List, float]:
    """
    Credit to Fillipe Goulart
    """
    # Get initial set {1, 2, ..., tsp_size} as a frozenset because @lru_cache
    # requires a hashable type
    N = frozenset(range(1, distance_matrix.shape[0]))
    memo: Dict[Tuple, int] = {}

    # Step 1: get minimum distance
    @lru_cache(maxsize=maxsize)
    def dist(ni: int, N: frozenset) -> float:
        if not N:
            return distance_matrix[ni, 0]

        # Store the costs in the form (nj, dist(nj, N))
        costs = [
            (nj, distance_matrix[ni, nj] + dist(nj, N.difference({nj})))
            for nj in N
        ]
        nmin, min_cost = min(costs, key=lambda x: x[1])
        memo[(ni, N)] = nmin

        return min_cost

    best_distance = dist(0, N)

    # Step 2: get path with the minimum distance
    ni = 0  # start at the origin
    solution = [0]

    while N:
        ni = memo[(ni, N)]
        solution.append(ni)
        N = N.difference({ni})

    return solution, best_distance
