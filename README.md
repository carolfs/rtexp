# rtexp

Code for the experiments in Feher da Silva, C.; Baldo, M. V. C. "Computational models of simple and choice reaction time tasks."

Copyright 2014, 2015 Carolina Feher da Silva

## License

rtexp is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

rtexp is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with rtexp.  If not, see <http://www.gnu.org/licenses/>.

## Test system

The experiments were tested on a 64-bit Linux system running Python 3.4.3
and graphviz 2.38.0.

## How to run the experiments

For the sensory model

1. cd to the rtexp directory
2. Run the experiment:

  ```
  $ python exp_bayesian_rt.py <s> <sigma> <tmax> <r> <acmin> <exp_type> [<REPS>]
  ```
  
  where:
  1. s: stimulus intensity, s > 0
  2. sigma: noise intensity, sigma > 0
  3. tmax: maximum time the target can appear
  4. r: probability that the target will appear
     on the left, given by a valid cue (0.5 < r ≤ 1)
  5. acmin: minimum accuracy (0 ≤ acmin ≤ 1)
  6. exp_type: experiment type (SRT or CRT)
  7. REPS: number of trials (REPS > 0)
3. The output is:
  - For simple RT experiments:
    * the proportion of correct and anticipated responses for valid trials
    * the proportion of correct and anticipated responses for neutral trials
    * the proportion of correct and anticipated responses for invalid trials
    * mean and standard error of RT for valid trials
    * mean and standard error of RT for neutral trials
    * mean and standard error of RT for invalid trials
  - For choice RT experiments:
    * the proportion of correct, wrong, anticipated, and missed responses for valid trials
    * the proportion of correct, wrong, anticipated, and missed responses for neutral trials
    * the proportion of correct, wrong, anticipated, and missed responses for invalid trials
    * mean and standard error of RT for valid trials
    * mean and standard error of RT for neutral trials
    * mean and standard error of RT for invalid trials

For the motor model
1. cd to the rtexp directory
2. Compile the integrate-and-fire network C++ module:
  
  ```
  $ python setup.py install --install-lib=.
  ```
3. Run the experiment using one of the configurations. For instance:

  ```
  $ python setup.py <exp1.cfg>
  ```
  
  The first figure in the article showing the motor model's results corresponds to configurations 1, 2, 7, and 8.
  The second figure corresponds to configurations 3, 4, 5, 6, 7, and 8.
4. Analyse the results:

  ```
  $ python analyse_motor.py <exp1.cfg>
  $ python rtss.py
  ```
5. Visualize network structure:

  ```
  $ python view_network.py <exp1.cfg> | dot -Tps -o <g1.ps>
  ```
  