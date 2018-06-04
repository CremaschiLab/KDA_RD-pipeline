# KDA_RD-pipebline
Knapsack problem based heuristic algorithms

# Summery
This repository contains the data and code needed to test a knapsack problem-based heuristic approach to phamarceutical R&D pipeline management.

Please note that Core is a work-in-progress. The current version as of June 04, 2018 has been copied into this repository for result reproducibility. An up-to-date version can be found at the public repo https://github.com/CremaschiLab/KDA_RD-pipebline

# Quickstart
###1. Cloning To obtain a copy of the source code

###2. Run

The command line example: python Solver.py solve-method=MSSP data-file=modeldata.dat min_solve

Solve-method: specific the solving methods, options: MSSP/KDA

Data-file: specific the test data file, which include in the Problem Files in this repository.

The additional options after test problems: min_solve/max_solve/greedy: specific different approaches for determining when knapsack problems are generated. The default option is the approach for knapsack problems generated after each realizations. The test can be found in: (Christian, B., & Cremaschi, S. (2017). Variants to a knapsack decomposition heuristic for solving R&D pipeline management problems. Computers & Chemical Engineering, 96, 18-32.)

###3. Example: the command line example can be found in: Command line entry. The example command line use the default knapsack problems generation approach.


# Data
The test data is in Problem Files

# Solver File
The solver file include both multistage stochastic programming model (MSSP) and knapsack problem-based heuristic approach (KDA) to phamarceutical R&D pipeline.

# Contact
For any questions, feel free to email szc0113@auburn.edu
