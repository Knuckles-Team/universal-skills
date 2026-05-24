---
name: personal_fitness_trainer
description: Assesses user fitness goals, queries appropriate strength training exercises, constructs a custom workout routine, and registers it using wger-agent tools.
domain: health
tags: ['health', 'workout', 'fitness', 'wger-agent']
requires: ['wger-agent']
---

# personal_fitness_trainer Workflow

Assesses user fitness goals, queries appropriate strength training exercises, constructs a custom workout routine, and registers it using wger-agent tools.

### Step 0: fitness-trainer
Conduct the user's fitness and muscle group intake assessment. Query the wger exercise database using wger_exercise tool with search query and muscle group parameters to discover target exercises.
Expected: intake, exercises

### Step 1: wger-agent
Create and configure a personal strength routine. Call the wger_routine tool to create a new routine, and then configure its workout days and exercises using the wger_routineconfig tool.
Expected: routine, configuration
Depends On: Step 0
