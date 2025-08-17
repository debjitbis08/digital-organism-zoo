import random

from genesis.environment import PatchGrid, SimpleEnvironment
from genesis.data_source import OfflineSampleDataSource


def test_logistic_regrowth_and_bounds():
    rng = random.Random(42)
    grid = PatchGrid(4, 4, K=10.0, r=0.3, noise_std=0.0, rng=rng)
    # Deplete a cell to near zero
    grid.set(1, 1, 0.1)
    # Step a few times; should increase but never exceed K
    for _ in range(20):
        grid.step_regrow()
        s = grid.get(1, 1)
        assert 0.0 <= s <= 10.0
    # A cell near K should not exceed K
    grid.set(2, 2, 9.9)
    for _ in range(5):
        grid.step_regrow()
        assert grid.get(2, 2) <= 10.0


def test_organism_eat_metabolize_and_reproduce():
    rng = random.Random(123)
    env = SimpleEnvironment(
        5,
        5,
        K=12.0,
        r=0.25,
        noise_std=0.0,
        bite=3.0,
        sense_radius=1,
        base_cost=0.1,
        mem_cost=0.02,
        signal_cost=0.01,
        signal_threshold=1.0,
        reproduce_threshold=8.0,  # low to trigger reproduction in test
        rng=rng,
        data_source=OfflineSampleDataSource(),
    )

    # Start one organism in the center with moderate energy and honesty 1.0 to simplify
    org = env.add_organism(2, 2, energy=6.0, M=3, epsilon=0.0, honesty=1.0)

    # Run a few steps; should eat and gain energy, then reproduce
    reproduced = False
    for _ in range(10):
        env.step()
        if len(env.organisms) > 1:
            reproduced = True
            break

    assert reproduced, "Organism should have reproduced under abundant conditions"
    # Parent and child should both be alive with positive energy
    assert all(o.energy > 0 for o in env.organisms)
    # Memory size mutation should be at most ±1
    parent = env.organisms[0]
    child = env.organisms[1]
    assert abs(child.M - parent.M) <= 1


def test_signaling_redirects_neighbors():
    rng = random.Random(999)
    env = SimpleEnvironment(
        5,
        5,
        K=15.0,
        r=0.3,
        noise_std=0.0,
        bite=5.0,
        sense_radius=1,
        base_cost=0.05,
        mem_cost=0.0,
        signal_cost=0.0,  # simplify budgeting
        signal_threshold=1.0,
        reproduce_threshold=9999.0,  # prevent reproduction here
        rng=rng,
    )
    # Two organisms: one will signal after a big bite; the other should redirect
    a = env.add_organism(2, 2, energy=2.0, M=0, epsilon=0.0, honesty=1.0)
    b = env.add_organism(1, 2, energy=2.0, M=0, epsilon=0.0, honesty=1.0)

    # Ensure center cell has a lot of stock so a takes a big bite and signals
    env.grid.set(2, 2, 10.0)
    # Run one step; b should get redirected toward (2,2) by the signal
    env.step()
    assert env.last_redirected >= 1


def test_regions_and_teacher_modulation_affect_regrowth():
    import statistics
    rng = random.Random(2024)
    env = SimpleEnvironment(6, 2, K=10.0, r=0.2, noise_std=0.0, rng=rng)
    # Define two regions: left (x<3) and right (x>=3)
    env.set_regions({'left': (0, 0, 3, 2), 'right': (3, 0, 6, 2)})
    # Apply teacher modulation: make right region have higher K and growth rate
    env.apply_teacher_modulation({'right': {'K': 20.0, 'r': 0.35}})
    # Run with no organisms for a while (pure regrowth)
    for _ in range(60):
        env.step()
    # Measure region averages
    left_vals = []
    right_vals = []
    for y in range(env.grid.height):
        for x in range(env.grid.width):
            s = env.grid.get(x, y)
            if x < 3:
                left_vals.append(s)
            else:
                right_vals.append(s)
    left_avg = statistics.mean(left_vals)
    right_avg = statistics.mean(right_vals)
    # Right region should have higher average stock due to higher K and r
    assert right_avg > left_avg + 2.0
