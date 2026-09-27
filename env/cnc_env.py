"""CNC machine scheduling environment.

The agent assigns jobs (parts to machine) to CNC machines one at a time.
Each job is appended to the end of the chosen machine's queue.

Job:     {"id", "duration", "part_size", "axes_needed", "deadline"}
Machine: {"id", "max_part_size", "axes"}
Action:  (job_id, machine_id)
"""

import copy


class CNCSchedulingEnv:
    def __init__(self, jobs, machines):
        """Store one task variant (its jobs and machines) and start an episode."""
        self.jobs = {j["id"]: j for j in jobs}
        self.machines = {m["id"]: m for m in machines}
        self.reset()

    def reset(self):
        """Clear the schedule and return the first observation."""
        self.schedule = []  # list of {"job_id", "machine_id", "start", "end"}
        self.machine_free = {m_id: 0 for m_id in self.machines}
        self.action_log = []
        self.done = False
        self.invalid = False
        return self._obs()

    def step(self, action):
        """Queue one job on one machine; return (observation, reward, done, info)."""
        if self.done:
            raise RuntimeError("Episode is over, call reset().")

        self.action_log.append(action)

        if not self._is_legal(action):
            # An illegal action ends the episode.
            self.invalid = True
            self.done = True
            return self._obs(), -1.0, True, {"invalid": True}

        job_id, machine_id = action
        job = self.jobs[job_id]
        start = self.machine_free[machine_id]
        end = start + job["duration"]
        self.machine_free[machine_id] = end
        self.schedule.append(
            {"job_id": job_id, "machine_id": machine_id, "start": start, "end": end}
        )

        reward = self._reward(job, machine_id, end)
        self.done = len(self.schedule) == len(self.jobs)
        return self._obs(), reward, self.done, {"invalid": False}

    def final_state(self):
        """Everything the verifier is allowed to see."""
        return copy.deepcopy(
            {
                "jobs": list(self.jobs.values()),
                "machines": list(self.machines.values()),
                "schedule": self.schedule,
                "action_log": self.action_log,
                "invalid": self.invalid,
            }
        )

    # --- internals ---------------------------------------------------------

    def _is_legal(self, action):
        """Structural legality only: known ids, job not scheduled yet.

        Compatibility (size, axes) is deliberately NOT enforced here, just as a
        real operator could load the wrong part. The verifier must catch it.
        """
        if not (isinstance(action, (tuple, list)) and len(action) == 2):
            return False
        job_id, machine_id = action
        if job_id not in self.jobs or machine_id not in self.machines:
            return False
        return job_id not in {s["job_id"] for s in self.schedule}

    def _reward(self, job, machine_id, end):
        """Per-step reward: 1 if this job is on time, else 0."""
        return 1.0 if end <= job["deadline"] else 0.0

    def _obs(self):
        """What the agent sees: unscheduled jobs and when each machine is free."""
        scheduled = {s["job_id"] for s in self.schedule}
        return {
            "unscheduled": [
                copy.deepcopy(j) for j_id, j in self.jobs.items() if j_id not in scheduled
            ],
            "machines": [
                {**m, "free_at": self.machine_free[m_id]}
                for m_id, m in self.machines.items()
            ],
        }
