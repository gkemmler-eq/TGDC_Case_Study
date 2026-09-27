"""Variant generator.

Builds a valid solution first (a planted schedule), then sets deadlines from it,
so every variant is guaranteed to be solvable.
"""

import math
import random

PRESETS = {
    "easy": {"n_jobs": 4, "n_machines": 2, "slack": 1.5, "seed": 1},
    "medium": {"n_jobs": 8, "n_machines": 3, "slack": 1.2, "seed": 2},
    "hard": {"n_jobs": 12, "n_machines": 4, "slack": 1.0, "seed": 3},
}


def generate(n_jobs, n_machines, slack, seed):
    """Create one variant: jobs, machines and a known-valid solution (list of actions)."""
    rng = random.Random(seed)

    machines = [
        {"id": m, "max_part_size": rng.randint(1, 3), "axes": rng.choice([3, 4, 5])}
        for m in range(n_machines)
    ]

    jobs, solution = [], []
    machine_free = [0] * n_machines
    for j in range(n_jobs):
        m = rng.randrange(n_machines)  # planted machine for this job
        machine = machines[m]
        duration = rng.randint(1, 6)
        machine_free[m] += duration
        jobs.append(
            {
                "id": j,
                "duration": duration,
                "part_size": rng.randint(1, machine["max_part_size"]),
                "axes_needed": rng.randint(3, machine["axes"]),
                "deadline": math.ceil(machine_free[m] * slack),
            }
        )
        solution.append((j, m))

    return {"jobs": jobs, "machines": machines, "solution": solution, "seed": seed}


def preset(name):
    """Return one of the predefined variants: 'easy', 'medium' or 'hard'."""
    return generate(**PRESETS[name])


def random_variant(seed=None):
    """Return a variant with random size and tightness, created at runtime.

    The seed is stored in the variant so any run can be reproduced.
    """
    if seed is None:
        seed = random.randrange(10**9)
    rng = random.Random(seed)
    return generate(
        n_jobs=rng.randint(4, 15),
        n_machines=rng.randint(2, 5),
        slack=rng.choice([1.0, 1.2, 1.5]),
        seed=seed,
    )
