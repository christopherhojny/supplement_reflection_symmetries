# Overview

This repository contains information about how to reproduce the numerical results presented in the article

> Detecting and Handling Reflection Symmetries in Mixed-Integer (Nonlinear) Programming

by Christopher Hojny. In the following, we explain which software is required to build the code and how to run numerical experiments to reproduce the numerical results of the article.

# I Installation

## Prerequisites

- clone the source code directory of [SCIP](https://github.com/scipopt/scip), in our experiments the code with githash [a93d088d](https://github.com/scipopt/scip/commit/a93d088d22b63194b842f658af7d20ab624a5dff) has been used
- install an LP solver, in the experiments, we have used [Soplex](https://github.com/scipopt/soplex) with githash [89ab43a9](https://github.com/scipopt/soplex/commit/89ab43a920b15667ad304305e9d22a31d3219efb)
- optional: install [Ipopt](https://coin-or.github.io/Ipopt/), in the experiments, we have used Ipopt 3.12

In the following, we assume that the cloned SCIP repository is contained in the directory `scip`.

## Installation Instructions

First, prepare the SCIP repository by applying a patch. The patch is used to print symmetry information to the terminal while solving an instance. This allows to evaluate which symmetries are detected for which instance. Except for providing this additional information, the patch does not change the behavior of SCIP. To apply the patch, use the following steps:

- copy the patch `patch_print_symmetry_statistics.txt` to the `scip` directory
- apply the patch by executing
> git apply patch_print_symmetry_statistics.txt

Second, install SCIP. For detailed instructions, we refer to the [installation instructions](https://github.com/scipopt/scip/blob/master/INSTALL.md) of SCIP. For our experiments, we have built SCIP using the following command from within the `scip` directory:

> make OPT=opt LPS=spx IPOPT=true

When Ipopt shall not be used, remove the corresponding option from the make command.

# II Generating and Getting Problem Instances

In the experiments described in the article, we have used publicly available instances as well as instances that we generated on our own. To reproduce the results, please download the following instance collections:

- [Color02](https://mat.tepper.cmu.edu/COLOR02/): Our test set consists of the instances collected at `Graph Coloring Instances`.
- [MIPLIB2017](https://miplib.zib.de/downloads/collection.zip)
- [MINLPLIB](http://minlplib.org/minlplib_osil.zip)
- [SAT2002](https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/New/Competition-02/sat-2002-beta.tgz): Our test sets consists of the contributed instances.

To generate our custom instances, create a directory `instances` within the directory `scripts_instances` and replace in `scripts_instances/generate_instances.py` the variable `color02path` by the absolute or relative path to the directory containing the `Color02` instances.

Finally, execute the script `generate_instances.py` to create the instances of the packing problem, kissing number problem, energy problem, and maxcut problem that we have used in our experiments. The instances are stored in CIP format in the newly created directory `instances`.

# III Running Experiments

## Running One Instance

To run the program, enter

> `scip/bin/scip.$(OSTYPE).$(ARCH).$(COMP).$(OPT).$(LPS).none`

(e.g. "bin/scip.linux.x86_64.gnu.opt.spx2.none") and provide the argument `-f <path/to/instance>` to specify an instance that shall be solved. An exemplary call is

> `./scip/bin/scip.linux.x86_64.gnu.opt.spx2.none -f <path/to/instance>`

Additional parameters can be:

- -s `<settingname>`
- -t `<timelimit>`
- -m `<memlimit>`
- -n `<nodelimit>`
- -d `<displayfrequency>`

# Running Automated Tests

To run automated tests, use from within the `scip` directory the command

>  `make OPT=opt LPS=spx IPOPT=true TEST=<testset> SETTINGS=<settingname> TIME=<timelimit> MEM=<memlimit> test`

where `<testset>` is the name of a test set of instances, `<settingname>` is the name of a file containing the parameter settings that shall be used, `<timelimit>` is the time limit per instance in seconds, and `<memlimit>` is the memory limit per instance in megabyte.

We assume that the directory `scip/check/testset` contains the file `testset.test` and that the directory `settings` contains the file `settingname.set`. Every line of a .test file contains the path to an instance of the test set. The paths need to be relative paths starting from the "check" directory. Symbolic links can be used to become more independent from the actual directory structure. A .set file contains in each line a parameter that shall be changed from its default value in the format

> `paramname = value`

The test set files used in our experiments are provided in the `testset` directory. For the benchmarking instances, we assume that symbolic links SAT, MINLP, and IP have been created (in the `scip/check` directory) that point to the directories containing the sat2002, minlplib, and miplib2017 instances, respectively. For the structured instances generated by ourselves, we assume that the corresponding directory `generated_instances` is contained in the `scip` directory.

The settings files of our experiments are provided in the settings directory.

# IV Evaluating Experiments

We assume that automated tests have been run to generate logs for the experiments of the different test sets. The script

> run_experiments.sh

in the main directory of this project can be used to run all experiments. Before executing it, copy it to the `scip` directory. The resulting log files are then stored in the directory

> `scip/check/results`

The directory

> scripts_experiments

contains scripts to generate the tables of the submission. By calling

> `python evaluate_running_times_nonlinear.py <path/to/log-directory> <testset>`

the table for the generated instances of the packing, kissing, and energy test set encoded in "testset.test" is generated. Note that the script assumes a specific name of the log files, among others, based on the computer architecture. To run the script on different computers, the names of the log files needs to be adjusted in the main function of the script.

By providing the optional parameter "--full", results on a per instance basis are generated; the optional parameter "--timelim `<value>`" can be used to specify the time limit per instance in seconds that has been used for the experiments. By default, the latter parameter has value 7200.

Calling

> `python evaluate_running_times_standard.py <path/to/log-directory> --tname <testset_1> ... --tname <testset_n>`

a table containing results for benchmarking instances is created. Here, multiple test sets can be summarized in the same table. The optional parameter "--timelim" can be used as before. Moreover, depending on the name of the log files, the file names encoded in the main function need to be adjusted.

To easily reproduce the tables, we have provided the logs of our experiments in the compressed directory `results.tar.gz`. This directory contains two sub directories `symmetry_statistics` and `performance`. The former contains logs of experiments in which each instance has just been presolved. These shorter runs are sufficient to get access to information about symmetries of the different instances. The directory `performance` contains the full logs of our experiments.