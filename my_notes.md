## My notes

1. Pick a task
2. Coding 5 parts (inspiration from hubbs5/or-gym)
    * env 
    * simple agent
    * verifier
    * data/problem generator
    * run script
3. Fix reward

### My Task

Machine scheduling (cnc known for delay)

CNC Machine scheduling:
 * Different lenghts of tasks
 * Different sizes (dimensions) of CNC parts
 * Different sizes of of machines
 * Different complexities of machines (how many axies a CNC machine has)

Success:
 * Every job on a compatible machine
 * No overlaps
 * Finish before deadline
 * Every job is scheduled once


### Coding

1. Env
    * problem statement: reset(), step(action), rewards, observations
    * from or-gym: initialize problem with data
    * check if a action is valid (not important for heuristic agent, but needed for general agents)
    * broken reward: only checks if task is finished before deadline

2. Agent
    * heuristic agent: take the first machine that is free and add next part there
    * later added: agent that first checks the part size and machine axies

3. Verifier
    * check if part to machine allocation is valid (size, axies)
    * check if no manufacturing time is overlapping 
    * check if parts are finished before deadline
    * check if parts are only added once not multiple times
    * later added: explanation why verifier failed

4. Data/problem generator
    * generate 3 problems: easy, medium, hard (#tasks, #machines, deadline strictness)
    * possability to randomly generate problems
    * later added: 5 predefined problems

5. Run script
    * Run all problems in episodes
    * Print reward and verifier score


### Fix reward

Now not only the deadline gets checked for 0/1 reward, but also if the part is on a compatible machine