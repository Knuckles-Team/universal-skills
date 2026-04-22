#!/usr/bin/env python3
try:
    import httpx
except ImportError:
    print("Error: Missing required dependencies for the 'agent-workflows' skill.")
    print(
        "Please install them by running: pip install 'universal-skills[agent-workflows]'"
    )
    import sys

    sys.exit(1)

import asyncio
import json
import uuid
import argparse
import sys
import os
import re


def parse_agents_md(agents_file_path: str, target_agent_name: str) -> str:
    """
    Parses an AGENTS.md file to find the URL for a given agent name.
    Expects a markdown table format with 'Name' and 'Endpoint URL' columns.
    """
    if not os.path.exists(agents_file_path):
        print(f"Error: AGENTS file not found at {agents_file_path}")
        return None

    try:
        with open(agents_file_path, "r") as f:
            lines = f.readlines()

        # Very permissive parsing: Look for lines that look like table rows
        # with our target agent name and a URL.
        # This regex matches a markdown table row, looking for the name in the first column
        # and a URL in the second column.
        pattern = re.compile(
            rf"\|\s*{re.escape(target_agent_name)}\s*\|\s*(http[s]?://[^\s|]+)\s*\|",
            re.IGNORECASE,
        )

        for line in lines:
            match = pattern.search(line)
            if match:
                return match.group(1).strip()

        print(f"Error: Agent '{target_agent_name}' not found in {agents_file_path}")
        return None

    except Exception as e:
        print(f"Error reading AGENTS file: {e}")
        return None


async def validate_agent_card(client, agent_url, print_card=False):
    """
    Validates the agent by fetching its well-known agent card.
    If print_card is True, fully outputs the card details.
    """
    card_url = f"{agent_url.rstrip('/')}/.well-known/agent-card.json"
    if print_card:
        print(f"Fetching agent card from: {card_url}\n")
    try:
        resp = await client.get(card_url)
        if resp.status_code == 200:
            try:
                card_data = resp.json()
                if print_card:
                    print("--- Agent Card Details ---")
                    print(json.dumps(card_data, indent=2))
                return True
            except json.JSONDecodeError:
                print(f"Failed to decode agent card JSON from {card_url}")
                return False
        else:
            print(f"Failed to fetch agent card. Status Code: {resp.status_code}")
            return False
    except httpx.RequestError as e:
        print(f"Connection failed to {card_url}: {e}")
        return False


async def list_tasks(client, agent_url):
    """
    Fetches the queue of tasks from the backend.
    """
    print(f"Fetching task queue from {agent_url}...\n")
    payload = {
        "jsonrpc": "2.0",
        "method": "tasks/list",
        "params": {},
        "id": 1,
    }

    try:
        resp = await client.post(
            agent_url, json=payload, headers={"Content-Type": "application/json"}
        )

        if resp.status_code != 200:
            print(f"Error fetching tasks. Status Code: {resp.status_code}")
            print(resp.text)
            return

        data = resp.json()
        if "error" in data:
            if data["error"].get("code") == -32601:
                print("Error: The agent does not support the 'tasks/list' method.")
            else:
                print(f"JSON-RPC Error: {data['error']}")
            return

        tasks = data.get("result", {}).get("tasks", [])
        if not tasks:
            print("No active tasks found in the queue.")
            return

        print("--- Task Queue ---")
        for task in tasks:
            t_id = task.get("id", "Unknown")
            state = task.get("status", {}).get("state", "Unknown")
            print(f"Task ID: {t_id} | State: {state}")

    except httpx.RequestError as e:
        print(f"Connection failed during tasks/list: {e}")
    except json.JSONDecodeError:
        print(f"Failed to decode response JSON: {resp.text}")


async def send_message(client, agent_url, message_text):
    """
    Sends a message to the agent via JSON-RPC.
    """
    print(f"\nSending Message: '{message_text}' to {agent_url}")

    payload = {
        "jsonrpc": "2.0",
        "method": "message/send",
        "params": {
            "message": {
                "kind": "message",
                "role": "user",
                "parts": [{"kind": "text", "text": message_text}],
                "messageId": str(uuid.uuid4()),
            }
        },
        "id": 1,
    }

    try:
        resp = await client.post(
            agent_url, json=payload, headers={"Content-Type": "application/json"}
        )

        if resp.status_code != 200:
            print(f"Error sending message. Status Code: {resp.status_code}")
            print(resp.text)
            return None

        data = resp.json()
        if "error" in data:
            print(f"JSON-RPC Error: {data['error']}")
            return None

        if "result" in data and "id" in data["result"]:
            task_id = data["result"]["id"]
            print(f"Task Submitted with ID: {task_id}")
            return task_id
        else:
            print(f"Unexpected response format: {data}")
            return None

    except httpx.RequestError as e:
        print(f"Connection failed during message send: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Failed to decode response JSON: {resp.text}")
        return None


async def poll_task(client, agent_url, task_id):
    """
    Polls the task status until completion.
    """
    print(f"Polling for result for Task ID: {task_id}...")

    while True:
        await asyncio.sleep(2)
        poll_payload = {
            "jsonrpc": "2.0",
            "method": "tasks/get",
            "params": {"id": task_id},
            "id": 2,
        }

        try:
            poll_resp = await client.post(
                agent_url,
                json=poll_payload,
                headers={"Content-Type": "application/json"},
            )

            if poll_resp.status_code != 200:
                print(f"Polling Failed: {poll_resp.status_code}")
                print(f"Details: {poll_resp.text}")
                break

            poll_data = poll_resp.json()

            if "error" in poll_data:
                print(f"Polling Error: {poll_data['error']}")
                break

            if "result" in poll_data:
                status = poll_data["result"].get("status", {})
                state = status.get("state")
                print(f"Task State: {state}")

                if state not in ["submitted", "running", "working"]:
                    print(f"\nTask Finished with state: {state}")
                    return poll_data["result"]
            else:
                print(f"Unexpected polling response: {poll_data}")
                break

        except httpx.RequestError as e:
            print(f"Connection failed during polling: {e}")
            break
        except json.JSONDecodeError:
            print(f"Failed to decode polling response: {poll_resp.text}")
            break


async def stream_task(client, agent_url, task_id):
    """
    Streams Server-Sent Events (SSE) updates for the task.
    """
    print(f"Streaming updates for Task ID: {task_id}...\n")

    payload = {
        "jsonrpc": "2.0",
        "method": "tasks/subscribe",
        "params": {"id": task_id},
        "id": 2,
    }

    try:
        async with client.stream(
            "POST",
            agent_url,
            json=payload,
            headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
        ) as response:
            if response.status_code != 200:
                print(f"Subscription Failed. Status Code: {response.status_code}")
                # Fallback to polling if streaming isn't supported
                if response.status_code in [404, 406]:
                    print(
                        "Streaming not supported on backend, falling back to polling."
                    )
                    return await poll_task(client, agent_url, task_id)
                return None

            print("--- Stream Connected ---")
            async for line in response.aiter_lines():
                line = line.strip()
                if not line:
                    continue

                if line.startswith("data:"):
                    data_str = line[5:].strip()
                    if data_str == "[DONE]":
                        print("\nStream closed by server.")
                        break

                    try:
                        event_data = json.loads(data_str)
                        # Minimal rendering of incoming events
                        print(
                            f"Event: {event_data.get('type', 'update')} - {json.dumps(event_data.get('data', {}))}"
                        )

                        if event_data.get("type") == "completed":
                            print("\nTask marked completed via stream.")
                            break
                    except json.JSONDecodeError:
                        print(f"Stream raw: {data_str}")

        print("\nStream finished, fetching final result...")
        return await poll_task(client, agent_url, task_id)

    except httpx.RequestError as e:
        print(f"Connection failed during streaming: {e}")
        return None


def print_result(result):
    """
    Prints the final result from the agent.
    """
    if not result:
        return

    history = result.get("history", [])
    if history:
        last_msg = None
        # Find the last message that is NOT from the user (i.e., the agent's response)
        for msg in reversed(history):
            if msg.get("role") != "user":
                last_msg = msg
                break

        if last_msg:
            print("\n--- Agent Response ---")
            if "parts" in last_msg:
                for part in last_msg["parts"]:
                    if "text" in part:
                        print(part["text"])
                    elif "content" in part:
                        print(part["content"])
            else:
                print(f"Final Message (No parts): {last_msg}")
        else:
            print("\n--- No Agent Response Found in History ---")


async def main():
    parser = argparse.ArgumentParser(
        description="A2A Client for communicating with other agents."
    )

    parser.add_argument(
        "--action",
        choices=["chat", "get-card", "list-tasks"],
        default="chat",
        help="The action to perform on the target agent (default: chat).",
    )
    # Make url optional, as we can now use agent-name
    parser.add_argument(
        "--url",
        required=False,
        help="The base URL of the A2A Agent (e.g., http://agent.arpa/a2a/). Use this OR --agent-name.",
    )
    parser.add_argument(
        "--agent-name",
        required=False,
        help="The name of the target agent to look up in AGENTS.md.",
    )
    parser.add_argument(
        "--agents-file",
        required=False,
        default="agent/AGENTS.md",
        help="Path to the AGENTS.md file (default: agent/AGENTS.md).",
    )
    parser.add_argument(
        "--query",
        required=False,
        help="The message/query to send to the agent (Required for 'chat' action).",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Use Server-Sent Events (SSE) streaming instead of polling for task status.",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable SSL certificate verification for httpx requests.",
    )

    args = parser.parse_args()

    if not args.url and not args.agent_name:
        parser.error("Either --url or --agent-name must be provided.")

    if args.action == "chat" and not args.query:
        parser.error("The --query argument is required when the action is 'chat'.")

    if args.url and args.agent_name:
        print("Warning: Both --url and --agent-name provided. Using --url.")
        agent_url = args.url
    elif args.url:
        agent_url = args.url
    else:
        print(f"Looking up agent '{args.agent_name}' in {args.agents_file}...")
        agent_url = parse_agents_md(args.agents_file, args.agent_name)
        if not agent_url:
            sys.exit(1)

    print("Initializing A2A Client...")
    print(f"Target Agent: {agent_url}")
    print(f"Action: {args.action}")
    if args.insecure:
        print("Warning: SSL verification is disabled (--insecure)")

    # httpx config
    verify_ssl = not args.insecure

    async with httpx.AsyncClient(timeout=60.0, verify=verify_ssl) as client:
        if args.action == "get-card":
            await validate_agent_card(client, agent_url, print_card=True)
            sys.exit(0)

        elif args.action == "list-tasks":
            await list_tasks(client, agent_url)
            sys.exit(0)

        elif args.action == "chat":
            query = args.query
            print(f"Query: {query}")

            # 1. Validate Agent (Silently)
            if not await validate_agent_card(client, agent_url, print_card=False):
                print("Agent validation failed. Aborting.")
                sys.exit(1)

            # 2. Send Message
            task_id = await send_message(client, agent_url, query)
            if not task_id:
                print("Failed to submit task. Aborting.")
                sys.exit(1)

            # 3. Stream or Poll for Result
            if args.stream:
                result = await stream_task(client, agent_url, task_id)
            else:
                result = await poll_task(client, agent_url, task_id)

            # 4. Print Result
            print_result(result)


if __name__ == "__main__":
    asyncio.run(main())
