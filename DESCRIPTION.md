# NAStJA

## Purpose

The NAStJA (Neoteric Autonomous Stencil code for Jolly Algorithms) framework provides an easy way to enable massively parallel simulations for a wide range of multi-physics applications based on stencil algorithms.  
NAStJA supports the development of parallel strategies for high-performance computing. Specifically, we use the NAStJA-CiS (Cells in Silico) application for the simulation of macroscopic tissues, composed of thousands to millions of cells, at subcellular resolution.
CiS combines a Cellular Potts Model (CPM) at the microscale with nutrient and signal exchange at the mesoscale and an agent-based layer at the macroscale. While this enables detailed capture of individual cell dynamics, the CPM layer is computationally intensive, and is therefore the main bottleneck.

The benchmark is designed to test the strong scaling behavior for the simulation of a simple system.

## Source

Archive Name: `nastja-bench.tar.gz`

The file holds sources of and configuration files for NAStJA in the `src/` directory, instructions to run the benchmark, and according JUBE scripts.

The included source code of NAStJA is equivalent to [Git commit hash b72c25ae](https://gitlab.com/nastja/nastja/-/tree/b72c25aed3586ae4e3db8cb37879899d94d7c9de).

## Building

NAStJA is built for sole CPU usage.

### Prerequisites

Building NAStJA requires the following dependencies

- CMake 3.10+
- C++14 compliant compiler:
  - Clang 6, 7, 8, 9
  - GCC 7, 8
- Message Passing Interface (MPI) library

Running tests and building the documentation has the following additional requirements

- doxygen
- jq

### Manual

To build NAStJA, use the standard CMake procedure

```
mkdir src/nastja/build && cd src/nastja/build
cmake ..
make
```

### Modification

- Changing the workload is not within scope.
- Floating point optimisation must not be set to `--ffast-math` or similar.
- The baseline is derived using the `-O3` options.
- The system size needs to remain at (720, 720, 1152) for the benchmark to be valid (see "Execution" below)

### JUBE

The JUBE step `compile` takes care of building the benchmark. It configures and builds the benchmark in accordance with the outlined flags above.

## Execution

Changing the workload is not within scope.

The executable of the NAStJA benchmark is `nastja` (if built through JUBE, it is located in the `src/nastja/build/` sub-folder). The path to the parameter file `config.json` needs to be provided as an argument at execution, using the `-c` flag.

A script called `calc_block_counts_and_sizes.py` is provided for convenience in `benchmark/eval` to calculate the required blockcounts and blocksizes for a given total number of CPU cores. For example, if `N_CPUs` is the overall number of CPU cores (i.e. the number of nodes multiplied with the number of CPU cores per node), then the script is to be called via

```
python3 ./benchmark/eval/calc_block_counts_and_sizes.py -u -N N_CPUs
```

If possible, this python script will update `src/config.json` with these new values. If no configuration is possible, you will need to change `N_CPUs`.

Using the script or manually defining the parameters, in any case, the following has to hold:

```
N_CPUs = blockcount[0] * blockcount[1] * blockcount[2]

blockcount[0] * blockSize[0] = 720
blockcount[1] * blockSize[1] = 720
blockcount[2] * blockSize[2] = 1152
```

If this is not the case, the benchmark will not be valid due to the deviating system size. Some example configurations for a system with 48 cores per node are as follows:

|Nodes | blockcount | blocksize|
|---|---|---|
|2|(4, 4, 6)|(180, 180, 192)|
|4|(4, 6, 8)|(180, 120, 144)|
|8 (default) |(6, 8, 8)|(120, 90, 144)|
|16|(8, 8, 12)|(90, 90, 96)|
|32|(8, 12, 16)|(90, 60, 72)|

For a system with 96 cores per node, this changes to:

|Nodes | blockcount | blocksize|
|---|---|---|
|2|(4, 6, 8)|(180, 120, 144)|
|4 |(6, 8, 8)|(120, 90, 144)|
|8 (default)|(8, 8, 12)|(90, 90, 96)|
|16|(8, 12, 16)|(90, 60, 72)|
|32|(12, 16, 16)|(60, 45, 72)|

## Parallelization

NAStJA utilizes MPI for parallelization. Depending on the use-case, the number and distribution of ranks can be arbitrarily chosen to ensure the best performance, and the number should be equal to 

```
blockcount[0]*blockcount[1]*blockcount[2].
```

Please note that using OpenMP will not work, and the program will instead run on a single CPU. 

### JUBE

The JUBE step `execute` calls the application with the correct modules. 
It also cares about the MPI distribution by submitting a script to the batch system. 
The latter is achieved by populating a batch submission script template (via `platform.xml`) 
with information specified in the top of the script relating to the number of nodes and tasks per node. 
Via dependencies, the JUBE step `execute` calls the JUBE step `compile` automatically.

To submit a full self-contained benchmark to the batch system, call `jube run benchmark/jube/default.xml`. 
JUBE will generate the necessary configuration and files, and submit the benchmark to the batch engine.  
After a run, JUBE can also be used to extract the runtime of the program (with `jube continue`, `jube analyse` and `jube result`).

## Command Line

Please call the benchmark with

```
[mpiexec] ./src/nastja/build/nastja -c config.json -o out0 > job.out
```

## Verification

The application should run through successfully without any exceptions or error codes generated. 

In addition, a script called `test_simu.py` is provided in `benchmark/eval` to test whether the simulation was executed correctly. It needs the Python package Pandas for execution. For convenience, it also extracts the reference metric (see below).

The run directory, in which `config.json`, `job.out`, and the folder `out0` are located, needs to be given as a parameter to `test_simu.py`. For example, if these are located in the directory `foo/bar`, then the script is to be called via

```
python3 ./benchmark/eval/test_simu.py foo/bar
```

If the simulation finished successfully, a file `results.csv` containing the reference metric will be generated in `foo/bar` in addition to it being printed to the screen.

## Results

The benchmark prints an average time per MC step into the log file. This value is to be multiplied by the number of MC steps, `N_steps`, to get the reference metric of the benchmark, `t_run`, the overall simulation time. For the benchmark, `N_steps` is set to 5050 and is not to be changed.

Using the `test_simu.py` script, the benchmark is checked for correctness and `t_run` is printed.

### JUBE

By using `jube continue` after the benchmark simulations have completed, the `check_output` step is triggered, which utilizes the aforementioned `test_simu.py` script.
Using `jube analyse` and a subsequent `jube result` then prints an overview table with the number of nodes, tasks per node, verification result (_1_ for passing verification), time per MC step, and overall simulation time `t_run`, the metric of this benchmark.

```
jube continue benchmark/jube/run/
jube result -a benchmark/jube/run
```

 Nodes | Tasks/Node | Threads/Task | Ran correctly | time per MC /s |     t_run |
|-------|------------|--------------|---------------|----------------|-----------|
|     8 |        128 |            1 |             1 |        0.05301 | 267.70101 |

Use `jube result -s csv [...]` to print a machine-readable CSV version of the table.

## Baseline

The baseline configuration must be chosen such that `t_run` is less than or equal to 268s. This value is achieved with 8 nodes on the JURECA-DC Cluster system at JSC.
