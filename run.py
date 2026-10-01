"""Run each baseline agent on every preset plus random variants and report success."""

import sys

from agents import GreedyAgent, GreedyAgentSophisticated
from env import PRESETS, CNCSchedulingEnv, preset, random_variant, explain

N_RANDOM = 100


def run_episode(variant, agent, reward="fixed"):
    """Play one episode; return (total reward, verifier score, failure reasons)."""
    env = CNCSchedulingEnv(variant["jobs"], variant["machines"], reward=reward)
    obs = env.reset()
    done, total_reward = False, 0.0
    while not done:
        obs, reward, done, _ = env.step(agent.act(obs))
        total_reward += reward
    score, reasons = explain(env.final_state())
    return total_reward, score, reasons


def main():
    """Build the variants, run the agent on each and print a summary."""
    args = sys.argv[1:]
    show_explanation = "explanation=true" in (a.lower() for a in args)
    positional = [a for a in args if "=" not in a]
    seed = int(positional[0]) if positional else 0
    variants = [("preset", name, preset(name)) for name in PRESETS]
    for i in range(N_RANDOM):
        v = random_variant(seed + i)
        variants.append(("random", f"random (seed {v['seed']})", v))

    summary = []
    for agent in [GreedyAgent(), GreedyAgentSophisticated()]:
        print(f"\n== {type(agent).__name__} ==")
        scores = []
        totals = {g: {"solved": 0, "cases": 0, "naive": 0.0, "fixed": 0.0, "max": 0} for g in ("preset", "random")}
        for group, name, v in variants:
            naive, _, _ = run_episode(v, agent, reward="naive")
            fixed, score, reasons = run_episode(v, agent, reward="fixed")
            scores.append(score)
            n = len(v["jobs"])
            t = totals[group]
            t["solved"] += score
            t["cases"] += 1
            t["naive"] += naive
            t["fixed"] += fixed
            t["max"] += n
            print(
                f"{name:28} jobs={n:2}  naive reward={naive:4.1f}/{n}  "
                f"fixed reward={fixed:4.1f}/{n}  verifier={score}"
            )
            if show_explanation:
                for r in reasons:
                    print(f"    - {r}")
        print(f"success rate: {sum(scores)}/{len(scores)}")
        summary.append((type(agent).__name__, totals))

    print(f"\n== Summary (presets + {N_RANDOM} random variants, seeds {seed}-{seed + N_RANDOM - 1}) ==")
    for agent_name, totals in summary:
        for group, t in totals.items():
            if not t["cases"]:
                continue
            m = t["max"]
            print(
                f"{agent_name:25} {group:7} solved {t['solved']:3}/{t['cases']:<3}  "
                f"naive reward {t['naive']:4.0f}/{m} ({t['naive'] / m:.0%})  "
                f"fixed reward {t['fixed']:4.0f}/{m} ({t['fixed'] / m:.0%})"
            )


if __name__ == "__main__":
    main()
