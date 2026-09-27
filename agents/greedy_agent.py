"""Naive baseline: jobs in ID order, each on the machine that is free first.

Ignores part size, axes and deadlines on purpose.
"""


class GreedyAgent:
    def act(self, obs):
        """Pick the lowest-ID unscheduled job and the earliest-free machine."""
        job = min(obs["unscheduled"], key=lambda j: j["id"])
        machine = min(obs["machines"], key=lambda m: (m["free_at"], m["id"]))
        return (job["id"], machine["id"])
