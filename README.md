# KDA_RD-pipeline
Knapsack problem based heuristic algorithms

## Summary
This repository contains the data and code needed to test a knapsack problem-based heuristic approach to phamaceutical R&D pipeline planning problems.

Please note that Core is a work-in-progress. The current version as of June 04, 2018 has been copied into this repository for result reproducibility. An up-to-date version can be found at the public repo https://github.com/CremaschiLab/KDA_RD-pipebline

## Quickstart
###1. Clone file to obtain a copy of the source code

###2. How to run algorithm <br />
The command line: python Solver.py solve-method=X data-file=Y Z <br />
Example: python Solver.py solve-method=MSSP data-file=modeldata.dat min_solve 

X: solving methods options <br />
* Option 1: MSSP<br />
* Option 2: KDA

Y: test data file options, which is included in the Problem Files in this repository <br />
* Option 1: modeldata.data <br />
* Option 2: modeldata3.data <br />
* Option 3: modeldata4.data <br />
 ...<br />
* (All test data files can be found in Problem Files) <br />
  *  Input details can be found in:<br />
     >Christian, B., & Cremaschi, S. (2017). <br />
     >Variants to a knapsack decomposition heuristic for solving R&D pipeline management problems. <br />
     >Computers & Chemical Engineering, 96, 18-32.

Z: different approach options for determining when knapsack problems are generated. The default option is the approach for knapsack problems generated after each realization. 
* Option 1: min_solve <br />
* Option 2: max_solve <br />
* Option 3: greedy
  *  The details of different approaches can be found in: <br />
     >Christian, B., & Cremaschi, S. (2017). <br />
     >Variants to a knapsack decomposition heuristic for solving R&D pipeline management problems. <br />
     >Computers & Chemical Engineering, 96, 18-32.


###3. Example: the command line example can be found in: Command line entry.<br />
The example command line uses the default knapsack problems generation approach.


## Data
The test data is in Problem Files

## Solver File
The solver file include both multistage stochastic programming model (MSSP) and knapsack problem-based heuristic approach (KDA) to phamaceutical R&D pipeline.

## Contact
For any questions, feel free to email szc0113@auburn.edu
