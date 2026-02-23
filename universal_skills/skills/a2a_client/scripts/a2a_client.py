#!/usr/bin/env python3
import asyncio
import httpx
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


async def validate_agent_card(client, agent_url):
    """
    Validates the agent by fetching its well-known agent card.
    """
    card_url = f"{agent_url.rstrip('/')}/.well-known/agent-card.json"
    print(f"Fetching agent card from: {card_url}")
    try:
        resp = await client.get(card_url)
        if resp.status_code == 200:
            try:
                card_data = resp.json()
                print(f"Agent Card Found: {json.dumps(card_data, indent=2)}")
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

    # print(f"\nFull Result Debug:\n{json.dumps(result, indent=2)}")


async def main():
    parser = argparse.ArgumentParser(
        description="A2A Client for communicating with other agents."
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
        "--query", required=True, help="The message/query to send to the agent"
    )

    args = parser.parse_args()

    if not args.url and not args.agent_name:
        parser.error("Either --url or --agent-name must be provided.")

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

    query = args.query

    print("Initializing A2A Client...")
    print(f"Target Agent: {agent_url}")
    print(f"Query: {query}")

    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. Validate Agent
        if not await validate_agent_card(client, agent_url):
            print("Agent validation failed. Aborting.")
            sys.exit(1)

        # 2. Send Message
        task_id = await send_message(client, agent_url, query)
        if not task_id:
            print("Failed to submit task. Aborting.")
            sys.exit(1)

        # 3. Poll for Result
        result = await poll_task(client, agent_url, task_id)

        # 4. Print Result
        print_result(result)


if __name__ == "__main__":
    asyncio.run(main())
