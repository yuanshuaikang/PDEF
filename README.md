# PDEF
## Probabilistic Distribution Evolution Framework for High-Utility Co-location Pattern Mining


This repository provides the source code, datasets, and experimental
configurations for the paper:

**PDEF: Probabilistic Distribution Evolution Framework for
High-Utility Co-location Pattern Mining**


## Overview

PDEF is a probabilistic framework for high-utility co-location pattern
(HUCP) mining. It employs probability distribution evolution to guide
feature combination sampling under a finite computational budget.

The framework integrates probability initialization, utility-aware
distribution updating, sample diversification, and adaptive sample-size
reduction to improve mining efficiency while maintaining high empirical
completeness.




## Datasets

PDEF is evaluated on three real-world POI datasets and three synthetic
datasets.


### Real-world datasets

The real-world datasets are constructed from publicly available
point-of-interest (POI) data collected from Beijing, Shenzhen, and
Shanghai.

Each spatial instance contains:

- feature label;
- instance identifier;
- two-dimensional coordinates.

The processed datasets used in the experiments are directly provided in
the `data/` directory.


### Synthetic datasets

The synthetic datasets are generated using a spatial co-location data
generator following the procedure described in the paper.

The recorded generator configurations are:

| Dataset | Configuration |
|---|---|
| Synthetic Dataset 1 | (0.25, 0.5, 5, 500) |
| Synthetic Dataset 2 | (0.25, 0.5, 2.5, 1000) |
| Synthetic Dataset 3 | (0.25, 0.5, 2.5, 2000) |

The generated synthetic datasets are fixed and directly used in all
experiments.


## External Utility Settings

External utility values are assigned at the feature level.
All instances belonging to the same feature share the same utility value.

The complete utility settings used in the experiments are provided below.
All compared algorithms use identical utility values for each dataset.


### Real Dataset 1

```python
Utility = {
    'A': 51, 'B': 82, 'C': 21, 'D': 40,
    'E': 23, 'F': 1237, 'G': 29, 'H': 22,
    'I': 37, 'J': 13, 'K': 29, 'L': 22,
    'M': 17, 'N': 41, 'O': 889, 'P': 2000,
    'Q': 35, 'R': 14, 'S': 27, 'T': 11,
    'U': 19, 'V': 30, 'W': 39, 'X': 11
}

### Real Dataset 2

```python
Utility = {
    'A': 51, 'B': 47, 'C': 33, 'D': 54,
    'E': 65, 'F': 78, 'G': 36, 'H': 42,
    'I': 53, 'J': 66, 'K': 74, 'L': 35,
    'M': 41, 'N': 56, 'O': 72, 'P': 59,
    'Q': 44, 'R': 50, 'S': 60, 'T': 70,
    'U': 80, 'V': 81, 'W': 82, 'X': 77,
    'Y': 74, 'Z': 70, 'a': 66, 'b': 72,
    'c': 81, 'd': 84, 'e': 69, 'f': 83,
    'g': 88, 'h': 65, 'i': 62
}

### Real Dataset 3

```python
Utility = {
    'A': 2, 'B': -10, 'C': 8, 'D': 4,
    'E': 1, 'F': 4, 'G': -5, 'H': 3,
    'I': 13, 'J': 3, 'K': 5, 'L': -14,
    'M': 8, 'N': 2, 'O': -6, 'P': 4
}

### Synthetic Dataset 1

```python
Utility = {
    'A': 5, 'B': 8, 'C': 6, 'D': 10,
    'E': 7, 'F': 12, 'G': 9, 'H': 4,
    'I': 11, 'J': 6, 'K': 8, 'L': 13,
    'M': 7, 'N': 5, 'O': 9
}

### Synthetic Dataset 2

```python
Utility = {
    'A': 12, 'B': 18, 'C': 7, 'D': 25,
    'E': 10, 'F': 45, 'G': 15, 'H': 8,
    'I': 32, 'J': 20, 'K': 14, 'L': 55,
    'M': 22, 'N': 9, 'O': 38, 'P': 16
}

### Synthetic Dataset 3

```python
Utility = {
    'A': 15, 'B': 30, 'C': 12, 'D': 45,
    'E': 20, 'F': 180, 'G': 25, 'H': 10,
    'I': 70, 'J': 35, 'K': 18, 'L': 250,
    'M': 55, 'N': 22, 'O': 120,
    'P': 40, 'Q': 15
}
