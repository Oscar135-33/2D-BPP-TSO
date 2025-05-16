Bidimensional Bin Packing Heuristic

Authors: Oscar Garza Hinojosa, Derek Alejandro Sauceda Morales, Guillermo Vladimir Flores Báez, Fernando Yahir García Dávila

Overview

This repository provides a Python implementation of a heuristic method for the Bidimensional Bin Packing Problem (2D-BPP). Our goal is to generate good and feasible packing solutions in reasonable computation times. We test performance and efficiency on 15 benchmark instances.

The project includes:

  Heuristic Packing Algorithm: First-fit decreasing placement with rotation and candidate management.
  
  Local Search Procedures: Two strategies (FirstImprovement and BestImprovement) to refine initial packings.
  
  Visualization: Optional plotting of bin layouts when the number of bins is ≤ 10.
  
  Results Export: JSON summaries for original and improved solutions.
  
  PDF Report: Detailed study and testing documented in the report.pdf file.

Prerequisites:

  Python 3.7+
  
  Required Packages: Install via pip:
  
  python -m pip install matplotlib
  
  (Optional) Spyder IDE for interactive editing and debugging.

Usage

Clone or Download
  
  git clone <repository-url>
  cd <repository-folder>
  
Prepare Instances
  
  Place your instance files under the instances/ directory (or any folder of your choice).

Each instance file should follow the format:
  
  Line 1: Number of rectangles (m)
  
  Line 2: Bin width and height
  
  Lines 3+: ID width height for each rectangle
  
  Run the Heuristic
  
  python heuristic.py
  
Interactive Prompts
  
  Enter full path of the instance file:
  Provide the path to the instance you want to test (e.g., instances/instance1.txt).
  
  Perform Local Search? (y/n):
  
  y to run a refinement search after initial packing.
  
  n to skip local search and finish.
  
  Specify Method: FirstImprovement or BestImprovement (fi/bi)?
  
  fi for First Improvement (stops at first gain).
  
  bi for Best Improvement (searches all moves for the best gain).
  
Output Files
  
  output_original.json: JSON summary of the initial solution.
  
  output_improved.json (if improved): JSON summary after local search.
  
Visualization

  If the solution uses 10 bins or fewer, a graphical plot of each bin will appear.
  
  For more than 10 bins, plotting is skipped automatically.
