# Source Code Root

This directory contains the main source code for the Darwin Evolution Simulator backend. It is organized into several key modules. The physics engine ground penetration issue has been resolved. The genetic algorithm implementation has been debugged, but a test file requires Master intervention.

## Files
- __init__.py - [FINISHED] Python package initializer
- main.py - [FINISHED] Main application entry point
- main.test.py - [FINISHED] Tests for main application
- src_README.md - [FINISHED] This README file, reflecting the completion of the physics fix and the status of the genetic algorithm debugging.

## Subdirectories
- api/ - [BEGUN] API layer with endpoints, currently implementing integration tests for ground penetration.
- creature/ - [FINISHED] Creature data models and logic; deep `clone()` method implemented and comprehensively tested.
- evolution/ - [BEGUN] Genetic algorithm implementation debugged; however, a test in genetic_algorithm_test.py is flawed and requires Master intervention.
- neural_network/ - [FINISHED] Neural network models and calculations; `clone()` method implemented and tested.
- orchestrator/ - [FINISHED] Simulation orchestration logic
- physics/ - [FINISHED] Pymunk physics simulation engine; ground penetration bug fixed and verified.