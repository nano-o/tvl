This repository contains Python code to check whether the Stellar network is intertwined by reduction to SAT.

Technically, we first express the intertwined property as a formula in a three-valued logic, and then we check the validity of that formula by reduction to SAT.
Explaining this is left as future work.

To try it:
```
docker pull giulianolosa/tvl:latest
docker run giulianolosa/tvl:latest
```

At this point, this is just a toy.
In practice, use [`fbas_analyzer`](https://github.com/trudi-group/fbas_analyzer) (which powers [stellarbeat](https://stellarbeat.io)).

# Explanation

How do we check with a SAT solver that a federated Byzantine agreement system (FBAS), like the Stellar network or the MobileCoin network, is intertwined?

Let's assume that we the network is voting, using the Stellar consensus protocol (SCP), on the next block to append to the Stellar blockchain, and suppose that there are two competing blocks that we denote by 0 and 1.
What are the possible end states of the voting process?

If you are familiar with SCP, you might know that two properties should hold in the end state, for every x in {0,1} and every validator v:
- P1(x,v): If v has a slice that unanimously decides x, then v also decides x
- P2(x,v): If v has a blocking set that unanimous decides x, then v also decides x

We can create a formula in propositional logic that encodes those rules as follows.
We let each validator correspond to a unique variable, and, for every validator v, we interpret v deciding 0 as v being false and v deciding 1 as v being true.
Then, for each validator v, we create the following formula: ...
Finally, we conjoin all the formulas.

Every assignment of the variables that satisfies our formula will give us a possible end state of the voting process.
Since two intertwined nodes can never disagree in SCP, we can check that the network is intertwined by asking a SAT solver whether, in every possible assignment and for every validators v and v', we have `(v /\ v') \/ (~v /\ ~v')`.

However, this does not quite work.
Consider the following network, which has a non-regular validator...
