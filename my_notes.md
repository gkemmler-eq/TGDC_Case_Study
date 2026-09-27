## My notes allong the way

1. Pick a task
2. 3 parts (env, agent, verifier)
    * env with init reset and step methods (inspiration from hubbs5/or-gym)
    * simple agent which checks for next availability of machine
    * verifier

### My Task

CNC Machine scheduling:
 - Different lenghts of tasks
 - Different sizes (dimensions) of CNC parts
 - Different sizes of of machines
 - Different complexities of machines (how many axies a CNC machine has)

Success:
 - Every job on a compatible machine
 - No overlaps
 - Finish before deadline
 - Every job is scheduled once
