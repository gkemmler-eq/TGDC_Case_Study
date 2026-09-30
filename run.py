"""Run each baseline agent on every preset plus random variants and report success."""

import sys

from agents import GreedyAgent, GreedyAgentSophisticated
from env import PRESETS, CNCSchedulingEnv, preset, random_variant, explain

N_RANDOM = 0


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
    seed = int(positional[0]) if positional else None
    variants = [(name, preset(name)) for name in PRESETS]
    for i in range(N_RANDOM):
        v = random_variant(None if seed is None else seed + i)
        variants.append((f"random (seed {v['seed']})", v))

    for agent in [GreedyAgent(), GreedyAgentSophisticated()]:
        print(f"\n== {type(agent).__name__} ==")
        scores = []
        for name, v in variants:
            naive, _, _ = run_episode(v, agent, reward="naive")
            fixed, score, reasons = run_episode(v, agent, reward="fixed")
            scores.append(score)
            n = len(v["jobs"])
            print(
                f"{name:28} jobs={n:2}  naive reward={naive:4.1f}/{n}  "
                f"fixed reward={fixed:4.1f}/{n}  verifier={score}"
            )
            if show_explanation:
                for r in reasons:
                    print(f"    - {r}")
        print(f"success rate: {sum(scores)}/{len(scores)}")


if __name__ == "__main__":
    main()
