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
