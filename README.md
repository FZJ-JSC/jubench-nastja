# JUPITER Benchmark Suite: NAStJA

[![DOI](https://zenodo.org/badge/831459311.svg)](https://zenodo.org/badge/latestdoi/831459311) [![Static Badge](https://img.shields.io/badge/DOI%20(Suite)-10.5281%2Fzenodo.12737073-blue)](https://zenodo.org/badge/latestdoi/764615316)

This benchmark is part of the [JUPITER Benchmark Suite](https://github.com/FZJ-JSC/jubench). See the repository of the suite for some general remarks.

This repository contains the NAStJA (CPU) benchmark. [`DESCRIPTION.md`](DESCRIPTION.md) contains details for compilation, execution, and evaluation.

The source code of NAStJA is included in the `./src/` subdirectory as a submodule from the upstream NAStJA repository at [gitlab.com/nastja/nastja](https://gitlab.com/nastja/nastja).

## Quickstart

```
# Run the benchmark using JUBE
jube run benchmark/jube/default.xml
jube continue benchmark/jube/run --id XYZ #Call this only once simulations are done, in case you use a queue such as slurm
jube result -a benchmark/jube/run --id XYZ
```

This will obtain the required sources from GitLab and perform a full build and
run the benchmark afterwards.

### Example Output

JUWELS Cluster for `jube run default.xml` produces the following
output

|   Nodes | Tasks/Node |  Threads/Task | Ran correctly | time per MC /s | t_run |
|---------|------------|---------------|---------------|----------------|-------|
| 8       |    48      |       1       |       1       |    0.4587      |   459 |

