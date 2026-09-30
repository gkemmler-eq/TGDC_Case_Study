"""Exploit test: the naive reward pays full marks for a wrong schedule; the fixed one does not."""

import pytest

from agents import GreedyAgent
from env import PRESETS, CNCSchedulingEnv, preset, random_variant, verify

VARIANTS = [preset(name) for name in PRESETS] + [random_variant(s) for s in range(10)]
IDS = list(PRESETS) + [f"random{s}" for s in range(10)]


def run(v, agent, reward):
    """Play one episode; return (total reward, verifier score)."""
    env = CNCSchedulingEnv(v["jobs"], v["machines"], reward=reward)
    obs, done, total = env.reset(), False, 0.0
    while not done:
        obs, r, done, _ = env.step(agent.act(obs))
        total += r
    return total, verify(env.final_state())


def test_exploit_naive_reward_pays_full_for_wrong_schedule():
    """The documented exploit: GreedyAgent ignores machine limits on 'easy',
    gets full naive reward, yet the verifier rejects the schedule."""
    v = preset("easy")
    reward, score = run(v, GreedyAgent(), "naive")
    assert reward == len(v["jobs"])
    assert score == 0


def test_fix_same_schedule_no_longer_gets_full_reward():
    v = preset("easy")
    reward, score = run(v, GreedyAgent(), "fixed")
    assert reward < len(v["jobs"])
    assert score == 0


@pytest.mark.parametrize("v", VARIANTS, ids=IDS)
def test_fixed_full_reward_iff_verifier_passes(v):
    """With the fix, full reward and a verifier score of 1 always agree."""
    reward, score = run(v, GreedyAgent(), "fixed")
    assert (reward == len(v["jobs"])) == (score == 1)


@pytest.mark.parametrize("v", VARIANTS, ids=IDS)
def test_planted_solution_gets_full_fixed_reward(v):
    """The fix does not punish correct schedules."""
    env = CNCSchedulingEnv(v["jobs"], v["machines"], reward="fixed")
    total = sum(env.step(a)[1] for a in v["solution"])
    assert total == len(v["jobs"])


def test_unknown_reward_mode_rejected():
    with pytest.raises(ValueError):
        CNCSchedulingEnv([], [], reward="other")
