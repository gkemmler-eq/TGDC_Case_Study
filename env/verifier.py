"""Verifier: reads only the final state and returns 1 (solved) or 0 (not solved)."""

from .cnc_env import CNCSchedulingEnv


def verify(state):
    """Return 1 if the schedule is complete, compatible, overlap-free, on time and replayable."""
    if state["invalid"]:
        return 0
    checks = [_all_jobs_once, _compatible, _no_overlap, _on_time, _replays]
    return int(all(check(state) for check in checks))


def _all_jobs_once(state):
    """Every job appears exactly once in the schedule."""
    scheduled = [s["job_id"] for s in state["schedule"]]
    return sorted(scheduled) == sorted(j["id"] for j in state["jobs"])


def _compatible(state):
    """Each part fits its machine and the machine has enough axes."""
    jobs = {j["id"]: j for j in state["jobs"]}
    machines = {m["id"]: m for m in state["machines"]}
    for s in state["schedule"]:
        job, machine = jobs[s["job_id"]], machines.get(s["machine_id"])
        if machine is None:
            return False
        if job["part_size"] > machine["max_part_size"] or job["axes_needed"] > machine["axes"]:
            return False
    return True


def _no_overlap(state):
    """No two jobs run on the same machine at the same time."""
    by_machine = {}
    for s in state["schedule"]:
        by_machine.setdefault(s["machine_id"], []).append((s["start"], s["end"]))
    for slots in by_machine.values():
        slots.sort()
        for (_, end_a), (start_b, _) in zip(slots, slots[1:]):
            if start_b < end_a:
                return False
    return True


def _on_time(state):
    """Every job finishes by its deadline and runs for exactly its duration."""
    jobs = {j["id"]: j for j in state["jobs"]}
    for s in state["schedule"]:
        job = jobs[s["job_id"]]
        if s["end"] - s["start"] != job["duration"] or s["end"] > job["deadline"]:
            return False
    return True


def _replays(state):
    """Replaying the action log in a fresh env must give the same schedule.

    Blocks a final state that was written directly instead of reached through step().
    """
    env = CNCSchedulingEnv(state["jobs"], state["machines"])
    for action in state["action_log"]:
        if env.done:
            return False
        env.step(tuple(action))
    return not env.invalid and env.schedule == state["schedule"]
