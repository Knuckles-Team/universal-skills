---
name: smart_home_automation_orchestrator
description: Interacts with Home Assistant using home-assistant-agent to read device states, query calendar schedules, and trigger specific smart home services, scenes, scripts, or events.
domain: infra
tags: ['home-assistant', 'iot', 'automation', 'scene-management', 'home-assistant-agent']
requires: ['home-assistant-agent']
---

# smart_home_automation_orchestrator Workflow

Interacts with Home Assistant using home-assistant-agent to read device states, query calendar schedules, and trigger specific smart home services, scenes, scripts, or events.

### Step 0: home-assistant-agent
Retrieve current device states, entity metrics, and active calendar event triggers using home_assistant_states list_states and home_assistant_calendar get_calendar_events tools. Target sensor context: {{task}}
Expected: sensor_states, calendar_schedules, target_devices

### Step 1: home-assistant-agent
Execute the smart home automation scene or service update. Call home_assistant_services call_service to trigger lighting, climate, script, or custom notification actions matching the target schedule and state.
Expected: automation_results, service_call_logs
Depends On: Step 0
