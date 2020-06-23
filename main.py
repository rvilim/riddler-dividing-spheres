import argparse
import math
import sys
from collections import defaultdict
import csv
from ortools.sat.python import cp_model


def solve(n_spheres, n_piles, num_search_workers):

    positioned = {}
    weights = [(i + 1) ** 3 for i in range(n_spheres)]

    # If the sum of the sphere weights cannot be evenly divided by the number of piles, we trivially cannot split them
    # equally
    if sum(weights) % n_piles != 0:
        raise ValueError

    if (sum(weights) // n_piles) % 2 == 0:
        if n_piles % 2 == 1 and math.ceil(n_spheres / 2) % 2 == 1:
            print(f"Parity check failed for n_spheres={n_spheres}, n_piles={n_piles}")
            raise ValueError
    elif n_piles % 2 != 1 and math.ceil(n_spheres / 2) % 2 == 1:
        print(f"Parity check failed for n_spheres={n_spheres}, n_piles={n_piles}")
        raise ValueError

    model = cp_model.CpModel()
    for sphere in range(n_spheres):
        for pile in range(n_piles):
            positioned[(sphere, pile)] = model.NewBoolVar(f"sphere {sphere} in pile {pile}")

    # The weights of the piles must be the same, and must be equal to the total sphere weight split n_piles wayscc
    group_weight = int(sum([weights[s] for s in range(n_spheres)]) / n_piles)
    for i in range(n_piles - 1):
        model.Add(sum(weights[s] * positioned[(s, i)] for s in range(n_spheres)) == group_weight)

    # Every sphere must be in exactly one pile
    for sphere in range(n_spheres):
        model.Add(sum(positioned[(sphere, pile)] for pile in range(n_piles)) == 1)

    # Put the first sphere in the first pile (symmetry breaking)
    model.Add(positioned[(n_spheres - 1, 0)] == True)

    print(f"Putting sphere {n_spheres - 1} in pile 0")
    # If the sum of the biggest two cubes is greater than the sum of the cubes divided by the number of piles, then these
    # two cubes cannot be in the same pile
    for n in range(1, n_piles):
        if n_piles < n_spheres:
            if sum(weights) / n_piles < (n_spheres - n) ** 3 + (n_spheres - n - 1) ** 3:
                print(
                    f"The {n}th and {n+1}th biggest spheres for n_piles={n_piles}, n_spheres={n_spheres} cannot be in the same group"
                )
                print(f"Putting sphere {n_spheres - n - 1} in pile {n}")
                model.Add(positioned[(n_spheres - n - 1, n)] == True)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = num_search_workers

    status = solver.Solve(model)

    solution = defaultdict(list)

    if status == cp_model.OPTIMAL:
        for pile in range(n_piles):
            for sphere in range(n_spheres):
                if solver.Value(positioned[(sphere, pile)]) == True:
                    solution[pile].append(sphere)

        return solution
    elif status == cp_model.FEASIBLE:
        pass
    elif status == cp_model.INFEASIBLE:
        pass
    elif status == cp_model.UNKNOWN:
        print("unknown")
        sys.exit(1)
    elif status == cp_model.MODEL_INVALID:
        print("invalid")
        sys.exit(1)
    raise ValueError


def volume_diameter(d):
    return (4.0 / 3) * math.pi * ((d / 2.0) ** 3)


def get_args():
    parser = argparse.ArgumentParser(description="How should we split up the gold balls?")

    parser.add_argument(
        "--find_minimum", action="store_true", help="Find the minimum number of balls needed to split into n_piles evenly"
    )
    parser.add_argument("--find_workable", action="store_true", help="Find all workable number of balls")
    parser.add_argument("--find_single", action="store_true", help="Find all workable number of balls")

    parser.add_argument("--min_piles", type=int, default=1)
    parser.add_argument("--max_piles", type=int, default=10)
    parser.add_argument("--max_spheres", type=int, default=100)
    parser.add_argument("--num_search_workers", type=int, default=8)
    parser.add_argument("--n_spheres", type=int, default=100)
    parser.add_argument("--n_piles", type=int, default=8)
    args = parser.parse_args()

    return args


def main():
    args = get_args()

    if args.find_minimum:
        for n_piles in range(args.min_piles, args.max_piles + 1):
            for n_spheres in range(n_piles, args.max_spheres):
                try:
                    solution = solve(n_spheres, n_piles, args.num_search_workers)

                    with open("mininum_balls.txt", "a") as f:
                        print(f"Minimum for {n_piles} is {n_spheres}")
                        f.write(f"Minimum for {n_piles} is {n_spheres}\n")
                        for i in range(n_piles):

                            print(f"Pile {i+1}: {[i+1 for i in solution[i]]}, ", end="")
                            print(f"Total Volume: {sum(volume_diameter(d+1) for d in solution[i]):.2f} cm^3")

                            f.write(f"Pile {i+1}: {[i+1 for i in solution[i]]}, ")
                            f.write(f"Total Volume: {sum(volume_diameter(d+1) for d in solution[i]):.2f} cm^3\n")
                        f.write("\n")
                        f.write("\n")
                        break
                except ValueError:
                    print(f"Not possible for n_spheres={n_spheres} and n_piles={n_piles}")

    if args.find_workable:
        for n_piles in range(1, args.max_piles + 1):
            for n_spheres in range(3, args.max_spheres):
                try:
                    solution = solve(n_spheres, n_piles, args.num_search_workers)
                    possible = True
                except ValueError:
                    possible = False

                with open("possible_balls.csv", "a") as f:
                    writer = csv.writer(f)
                    writer.writerow((n_piles, n_spheres, possible))

    if args.find_single:
        try:
            solution = solve(args.n_spheres, args.n_piles, args.num_search_workers)

            print(f"Minimum for {args.n_piles} is {args.n_spheres}")
            for i in range(args.n_piles):

                print(f"Pile {i+1}: {[i+1 for i in solution[i]]}, ", end="")
                print(f"Total Volume: {sum(volume_diameter(d+1) for d in solution[i]):.2f} cm^3")

        except ValueError:
            print(f"{args.n_spheres} spheres in {args.n_piles} piles is not possible")


if __name__ == "__main__":
    main()
