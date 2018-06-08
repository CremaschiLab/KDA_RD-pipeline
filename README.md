# KDA_RD-pipeline
Knapsack problem-based Decomposition Algorithm (KDA)

## Summary
This repository contains the code for solving phamaceutical R&D pipeline clinical trial planning problem using Knapsack problem-based Decomposition Algorithm (KDA) and the data to replicate the results of 
  >Christian, B., & Cremaschi, S. (2017). <br />
  >Variants to a knapsack decomposition heuristic for solving R&D pipeline management problems. <br />
  >Computers & Chemical Engineering, 96, 18-32. 

Please note that Core is a work-in-progress. The current version as of June 04, 2018 has been copied into this repository for result reproducibility. An up-to-date version can be found at the public repo https://github.com/CremaschiLab/KDA_RD-pipeline

## Quickstart
###1. Clone file to obtain a copy of the source code

###2. How to run algorithm <br />
The command line: python Solver.py solve-method=X data-file=Y Z <br />
Example: python Solver.py solve-method=MSSP data-file=modeldata.dat min_solve 

X: speficies the approach that is used to solve the problem. Option MSSP generates the determinisitic equivalent of the multistage stochastic programming (MMSP) model and solves it using CPLEX. Option KDA uses the knapsack-problem based decomposition approach to solve the problem. <br />
* Option 1: MSSP<br />
* Option 2: KDA

Y: specifies the test data file, which is included in the Problem Files in this repository. The test data files include the parameter values of instances that were solved. <br />
* Option 1: modeldata.data <br />
* Option 2: modeldata3.data <br />
* Option 3: modeldata4.data <br />
 ...<br />
* (All test data files can be found in Problem Files) <br />
  *  Input details can be found in:<br />
     >Christian, B., & Cremaschi, S. (2017). <br />
     >Variants to a knapsack decomposition heuristic for solving R&D pipeline management problems. <br />
     >Computers & Chemical Engineering, 96, 18-32.

Z: speficies the approach to be used in KDA for generating knapsack sub-problems. The default option is min_solve, which generates knapsack sub-problems after each realization. Option max_solve generates knapsack sub-problems at time periods where theyre are no active clinical trials (or projects). Option greedy generates knapsack sub-problems at every time period.
* Option 1: min_solve <br />
* Option 2: max_solve <br />
* Option 3: greedy
  *  Details of different approaches can be found in: <br />
     >Christian, B., & Cremaschi, S. (2017). <br />
     >Variants to a knapsack decomposition heuristic for solving R&D pipeline management problems. <br />
     >Computers & Chemical Engineering, 96, 18-32.


###3. Example: the command line example can be found in: Command line entry.<br />
The example command line uses the default knapsack problems generation approach.


## Data
The test data is in Problem Files.

## Solver File
The solver file includes both the multistage stochastic programming model and the knapsack problem-based decomposition algorithm  to solve phamaceutical R&D pipeline clinical trial plannning problem.

## Contact
For any questions, feel free to email szc0113@auburn.edu
