"""Feasibility-aware baseline: jobs in ID order, each on the earliest-free machine
that can actually handle the part (fits and has enough axes).

Still ignores deadlines.
"""


class GreedyAgentSophisticated:
    def act(self, obs):
        """Pick the lowest-ID unscheduled job and the earliest-free compatible machine."""
        job = min(obs["unscheduled"], key=lambda j: j["id"])
        feasible = [m for m in obs["machines"] if self._fits(job, m)]
        # Fall back to all machines if none fits (the verifier will then score 0).
        machine = min(feasible or obs["machines"], key=lambda m: (m["free_at"], m["id"]))
        return (job["id"], machine["id"])

    @staticmethod
    def _fits(job, machine):
        """True if the part fits the machine and the machine has enough axes."""
        return (
            job["part_size"] <= machine["max_part_size"]
            and job["axes_needed"] <= machine["axes"]
        )
