# Wger MCP Reference

**Project:** `wger-agent`
**Entrypoint:** `wger-mcp`

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `WGER_INSTANCE` | Wger instance URL (default: https://wger.de) |
| `WGER_ACCESS_TOKEN` | Permanent API token for authentication |

## Available Tool Tags (7)

| Env Variable | Default |
|-------------|----------|
| `ROUTINETOOL` | `True` |
| `ROUTINECONFIGTOOL` | `True` |
| `EXERCISETOOL` | `True` |
| `WORKOUTTOOL` | `True` |
| `NUTRITIONTOOL` | `True` |
| `BODYTOOL` | `True` |
| `USERTOOL` | `True` |

## Stdio Connection (Default)

```json
{
  "mcpServers": {
    "wger-agent": {
      "command": "wger-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "WGER_INSTANCE": "${WGER_INSTANCE}",
        "WGER_ACCESS_TOKEN": "${WGER_ACCESS_TOKEN}",
        "ROUTINETOOL": "True",
        "ROUTINECONFIGTOOL": "True",
        "EXERCISETOOL": "True",
        "WORKOUTTOOL": "True",
        "NUTRITIONTOOL": "True",
        "BODYTOOL": "True",
        "USERTOOL": "True"
      }
    }
  }
}
```

## HTTP Connection

```json
{
  "mcpServers": {
    "wger-agent": {
      "url": "http://wger-agent:8787/mcp",
      "timeout": 200000
    }
  }
}
```

## Single-Tag Config Example

Enable only `EXERCISETOOL` and disable all others:

```json
{
  "mcpServers": {
    "wger-agent": {
      "command": "wger-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "WGER_INSTANCE": "${WGER_INSTANCE}",
        "WGER_ACCESS_TOKEN": "${WGER_ACCESS_TOKEN}",
        "ROUTINETOOL": "False",
        "ROUTINECONFIGTOOL": "False",
        "EXERCISETOOL": "True",
        "WORKOUTTOOL": "False",
        "NUTRITIONTOOL": "False",
        "BODYTOOL": "False",
        "USERTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List all tools
python scripts/mcp_client.py --config references/wger-agent.json --action list-tools

# Generate a single-tag config
python scripts/mcp_client.py --action generate-config \
    --mcp-command wger-mcp \
    --enable-tag EXERCISETOOL \
    --all-tags "ROUTINETOOL,ROUTINECONFIGTOOL,EXERCISETOOL,WORKOUTTOOL,NUTRITIONTOOL,BODYTOOL,USERTOOL"
```

## Tailored Skills Reference

### wger-routine

**Description:** "Manage workout routines, days, slots, slot entries, and templates."

#### Available Tools
- `get_routines`: List all workout routines.
- `get_routine`: Get a specific routine by ID.
- `create_routine`: Create a new workout routine.
  - **Parameters**: `name` (str), `description` (str), `start_date` (str), `end_date` (str), `fit_in_week` (bool)
- `delete_routine`: Delete a routine.
- `get_days`: List workout days.
- `create_day`: Create a workout day in a routine.
  - **Parameters**: `routine` (int), `name` (str), `is_rest` (bool), `order` (int), `day_type` (str)
- `delete_day`: Delete a workout day.
- `get_slots`: List exercise slots (sets).
- `create_slot`: Create an exercise slot in a day.
  - **Parameters**: `day` (int), `order` (int), `slot_type` (str)
- `create_slot_entry`: Add an exercise to a slot.
  - **Parameters**: `slot` (int), `exercise` (int), `order` (int)
- `get_templates`: List user's workout templates.
- `get_public_templates`: List publicly shared workout templates.

### wger-routine-config

**Description:** "Configure weight, repetitions, sets, rest, and RiR progression rules."

#### Available Tools
- `create_weight_config`: Create weight progression config.
  - **Parameters**: `slot_entry` (int), `iteration` (int), `value` (float), `operation` (str: r/+/-), `step` (str: abs/percent), `repeat` (bool)
- `get_weight_configs`: List weight configs.
- `create_repetitions_config`: Create repetitions progression config.
- `get_repetitions_configs`: List repetitions configs.
- `create_sets_config`: Create sets count progression config.
- `create_rest_config`: Create rest time progression config.
- `create_rir_config`: Create RiR (Reps in Reserve) progression config.

### wger-exercise

**Description:** "Browse the exercise database — categories, muscles, equipment, images, variations."

#### Available Tools
- `get_exercises`: List exercises. Filters: language, category, muscles, equipment.
- `get_exercise_info`: Get detailed exercise info (images, muscles, equipment).
  - **Parameters**: `exercise_id` (int)
- `search_exercises`: Search exercises by name.
  - **Parameters**: `term` (str), `language` (int), `limit` (int)
- `get_exercise_categories`: List categories (Arms, Legs, Chest, etc.).
- `get_equipment`: List equipment (Barbell, Dumbbell, etc.).
- `get_muscles`: List muscles (Biceps, Quadriceps, etc.).
- `get_exercise_images`: List exercise images.
- `get_variations`: List exercise variation groups.

### wger-workout

**Description:** "Log workout sessions and individual sets."

#### Available Tools
- `get_workout_sessions`: List workout sessions.
- `get_workout_session`: Get a specific session.
- `create_workout_session`: Create a workout session.
  - **Parameters**: `routine` (int), `date` (str), `impression` (str: 1-5), `notes` (str)
- `delete_workout_session`: Delete a session.
- `get_workout_logs`: List workout log entries.
- `create_workout_log`: Log a set (exercise, weight, reps).
  - **Parameters**: `exercise` (int), `routine` (int), `date` (str), `repetitions` (int), `weight` (float)
- `delete_workout_log`: Delete a log entry.

### wger-nutrition

**Description:** "Manage nutrition plans, meals, ingredients, and food diary."

#### Available Tools
- `get_nutrition_plans`: List nutrition plans.
- `get_nutrition_plan_info`: Get detailed plan with meals and nutritional totals.
- `create_nutrition_plan`: Create a plan with macro goals.
  - **Parameters**: `description` (str), `goal_energy` (float), `goal_protein` (float), `goal_carbohydrates` (float), `goal_fat` (float)
- `delete_nutrition_plan`: Delete a plan.
- `create_meal`: Create a meal in a plan.
  - **Parameters**: `plan` (int), `name` (str), `time` (str)
- `create_meal_item`: Add an ingredient to a meal.
  - **Parameters**: `meal` (int), `ingredient` (int), `amount` (float)
- `get_ingredients`: List/search ingredients.
- `get_ingredient_info`: Get detailed ingredient nutritional info.
- `get_nutrition_diary`: List nutrition diary entries.
- `log_nutrition`: Log food eaten.

### wger-body

**Description:** "Track body weight, measurements, and progress photos."

#### Available Tools
- `get_weight_entries`: List body weight entries.
- `log_body_weight`: Log a body weight entry.
  - **Parameters**: `date` (str), `weight` (float)
- `delete_weight_entry`: Delete a weight entry.
- `get_measurements`: List body measurements.
- `log_measurement`: Log a body measurement.
  - **Parameters**: `category` (int), `date` (str), `value` (float)
- `get_measurement_categories`: List categories (Biceps, Chest, etc.).
- `create_measurement_category`: Create a new category.
- `get_gallery`: List progress photos.

### wger-user

**Description:** "User profile, statistics, trophies, and settings."

#### Available Tools
- `get_user_profile`: Get user profile (age, height, gender).
- `get_user_statistics`: Get workout statistics.
- `get_user_trophies`: List earned trophies.
- `get_languages`: List available languages.
- `get_repetition_units`: List repetition unit settings.
- `get_weight_unit_settings`: List weight unit settings.
