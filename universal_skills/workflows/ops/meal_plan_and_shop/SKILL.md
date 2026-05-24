---
name: meal_plan_and_shop
description: Parallel execution workflow for meal plan and shop using the Unified Parallel Engine
domain: ops
tags:
  - parallel-workflow
  - ops
  - mcp-mealie
---

# Parallel Workflow: Meal Plan And Shop

This workflow defines the topological parallel execution steps for meal plan and shop.

## Steps

### Step 1: preferences
Execute the preferences phase for the meal_plan_and_shop workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: preferences_artifacts
### Step 2: generate_plan [depends_on: preferences]
Execute the generate plan phase for the meal_plan_and_shop workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: generate_plan_artifacts
### Step 3: scale_recipes [depends_on: generate_plan]
Execute the scale recipes phase for the meal_plan_and_shop workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: scale_recipes_artifacts
### Step 4: shopping_list [depends_on: scale_recipes]
Execute the shopping list phase for the meal_plan_and_shop workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: shopping_list_artifacts
### Step 5: add_to_mealie [depends_on: shopping_list]
Execute the add to Mealie phase for the meal_plan_and_shop workflow under the ops domain. This involves orchestrating the designated specialists to process inputs, configure tools, and perform targeted operations.
Expected: add_to_mealie_artifacts
