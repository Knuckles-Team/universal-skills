---
name: dietician_and_chef
description: Generates a customized healthy meal plan, adds selected recipes, and compiles an organized, scaled household shopping list in Mealie using mealie-mcp tools.
domain: health
tags: ['health', 'diet', 'recipes', 'mealie-mcp']
requires: ['mealie-mcp']
---

# dietician_and_chef Workflow

Generates a customized healthy meal plan, adds selected recipes, and compiles an organized, scaled household shopping list in Mealie using mealie-mcp tools.

### Step 0: dietician-chef
Generate a customized weekly meal plan matching the user's calorie targets. Register/add the planned meals to Mealie using the mealie_recipes and mealie_organizer tools.
Expected: mealplan, recipes

### Step 1: mealie-mcp
Compile and organize a consolidated grocery shopping list for the planned weekly meals. Use the mealie_households tools to add the required recipe ingredients scaled for the household into a clean, categorized Mealie shopping list.
Expected: shopping_list, ingredients
Depends On: Step 0
