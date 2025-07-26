# Genetic Algorithm Module

- **Purpose**: To evolve the population of creatures.
- **Key Interfaces**: `evolve_population(population, settings)`
- **Dependencies**: Creature Module

## Files
- genetic_algorithm.py - [BEGUN] Main implementation of genetic algorithm logic, uses single-parent reproduction and `elitism_count` from settings.
- genetic_algorithm_test.py - [BEGUN] Tests for genetic algorithm. Needs critical fixes for its ID tracking assertion logic in `test_single_parent_reproduction_rigorous_id_tracking`.