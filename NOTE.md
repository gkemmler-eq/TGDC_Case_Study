# Note: CNC scheduling environment with a broken reward

## Decisions

- **Task: CNC machine scheduling.** 
    * Jobs have a duration, part size, number of axes needed and a deadline. 
    * Machines have a maximum part size and a number of axes. 
    * The agent assigns one job per step, and the job is added to the end of that machine's queue. 
    * I picked this task because in my experience CNC parts need lots of time to get from order to shipped part and the scheduling might need some improvement.
- **Compatibility checks** 
    * In step(), the agent can take incompatible actions, only the verifier at the end will check for full consistency
    * The verifier replays the action log, so a goal state written directly scores 0.
- **Generated cases** 
    * 5 fixed test cases with varying difficulty
    * Possibility to create more random test cases for better evaluation of agents.
    * Every case is solvable: it is built around a known valid schedule.
- **2 heuristic agents**
    * simple one, that just takes the next free machine
    * a more sophisticated one, that also checks for compatibility with the machine
- **Test cases for the verifier/rewards**
    * in tests/ the verifier and the reward get tested so that one can detect if they break during changes in the future

## Results

Baselines over 5 presets and 100 seeded random variants (`python run.py`, seeds 0–99; see the summary at the end of its output):

| Agent | Presets (Verifier Score) | Presets (Reward broken / fixed) | Random (Verifier Score) | Random (Reward broken / fixed) |
|---|---|---|---|---|
| GreedyAgent  | 0/5 | 43/49 (88%) / 36/49 (73%) | 4/100 | 788/925 (85%) / 612/925 (66%) |
| GreedyAgentSophisticated  | 2/5 | 40/49 (82%) / 40/49 (82%) | 34/100 | 783/925 (85%) / 783/925 (85%) |

Reward is summed over all variants; the maximum is one point per job.

With the broken reward, the GreedyAgent gets as much or more reward than the better one, even though it almost never solves a case. It even gets full reward on 34 random cases that the verifier rejects. With the fixed reward, GreedyAgent drops (88% → 73% on presets), while the better agent keeps its reward, because it never puts a part on the wrong machine.

**The broken reward.** 
 * The first reward gave +1 for each job that finished on time and ignored whether the part fits the machine.

**The fix.** 
 * A job earns +1 only if it is on time and on a compatible machine. Because step() makes overlaps impossible, full reward now means exactly that the verifier passes.

## Limits

* The model is simplified: no setup time, no machine downtime, no jobs arriving during the episode, and no priorities.
* The reward is still sparse and per-job. It gives no credit for getting close to a deadline, which may make learning slow.
* The baselines never try to meet deadlines, so they show what an agent can't do, not how hard the task actually is.

## Next step: what a buyer would need

Most likely the buyer is a lab training or evaluating agents. They would need:

* An interface for agents to use the system
    * State and actions as text/JSON, so LLM agents can read the jobs and send actions
    * A clear error message for invalid actions instead of just ending the episode
* A way to use real world data
    * An importer for company data (orders, machines, deadlines)
    * Compare generated cases with real ones to see if they look alike
* More realism in the data
    * Part sizes in 3D instead of one number
    * Setup times between jobs, machine downtime, jobs arriving during the day, priorities
* Protection against broken rewards
    * Automatically flag every run where reward and verifier disagree, this is how the exploit here shows up
    * Keep a set of hidden cases that agents are never trained on