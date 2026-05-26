#!/usr/bin/env python3
import os
import sys
import yaml
import json
import time
import requests
import subprocess
import logging
import argparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class GitOpsSyncer:
    def __init__(self, gitlab_url, gitlab_token, portainer_url, portainer_token, endpoint_id="3"):
        self.gitlab_url = gitlab_url.rstrip('/')
        self.gitlab_token = gitlab_token
        self.portainer_url = portainer_url.rstrip('/')
        self.portainer_token = portainer_token
        self.endpoint_id = endpoint_id
        
        self.gitlab_headers = {"PRIVATE-TOKEN": self.gitlab_token}
        self.portainer_headers = {"Authorization": f"Bearer {self.portainer_token}"}

    def parse_inventory(self, inventory_path):
        """Parses inventory.yml/yaml file to extract host lists and IPs."""
        if not os.path.exists(inventory_path):
            logging.warning(f"Inventory file not found at {inventory_path}. Skipping node scanning.")
            return {}
            
        logging.info(f"Scanning host inventory file: {inventory_path}")
        try:
            with open(inventory_path, "r") as f:
                content = yaml.safe_load(f)
            # Standard Ansible inventory parser
            nodes = {}
            all_groups = content.get("all", {}).get("children", {}) or content
            for group, gdata in all_groups.items():
                hosts = gdata.get("hosts", {}) if isinstance(gdata, dict) else gdata
                if not hosts:
                    continue
                for host, hdetails in hosts.items():
                    ip = hdetails.get("ansible_host") or hdetails.get("ip") if isinstance(hdetails, dict) else host
                    nodes[host] = {
                        "ip": ip,
                        "group": group,
                        "details": hdetails
                    }
            logging.info(f"Discovered {len(nodes)} active hardware nodes from inventory.")
            return nodes
        except Exception as e:
            logging.error(f"Failed to parse inventory: {e}")
            return {}

    def parse_workspace(self, workspace_path):
        """Parses workspace.yml to extract repository locations and project contexts."""
        if not os.path.exists(workspace_path):
            logging.warning(f"Workspace file not found at {workspace_path}. Skipping repository scanning.")
            return []
            
        logging.info(f"Scanning workspace file: {workspace_path}")
        try:
            with open(workspace_path, "r") as f:
                content = yaml.safe_load(f)
            repositories = content.get("repositories", []) or []
            logging.info(f"Discovered {len(repositories)} active workspaces / repositories.")
            return repositories
        except Exception as e:
            logging.error(f"Failed to parse workspace config: {e}")
            return []

    def run_git(self, cmd, cwd):
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"Git execution error: {' '.join(cmd)} in {cwd}. Error: {result.stderr}")
            return False
        return True

    def sync_to_gitlab(self, local_path, service_name, gitlab_project_path):
        encoded_path = gitlab_project_path.replace('/', '%2F')
        url = f"{self.gitlab_url}/api/v4/projects/{encoded_path}"
        res = requests.get(url, headers=self.gitlab_headers)
        
        if res.status_code == 404:
            logging.info(f"Creating project on GitLab: {gitlab_project_path}...")
            create_url = f"{self.gitlab_url}/api/v4/projects"
            parts = gitlab_project_path.split('/')
            namespace_path = parts[0]
            
            grp_res = requests.get(f"{self.gitlab_url}/api/v4/groups/{namespace_path}", headers=self.gitlab_headers)
            if grp_res.status_code != 200:
                logging.error(f"Group/Namespace {namespace_path} not found on GitLab.")
                return False
            
            group_id = grp_res.json()["id"]
            payload = {
                "name": service_name,
                "path": service_name,
                "namespace_id": group_id,
                "visibility": "private"
            }
            create_res = requests.post(create_url, headers=self.gitlab_headers, json=payload)
            if create_res.status_code != 201:
                logging.error(f"Failed to create GitLab project: {create_res.text}")
                return False
            project_info = create_res.json()
        else:
            project_info = res.json()

        http_url = project_info["http_url_to_repo"]
        auth_url = http_url.replace("http://", f"http://oauth2:{self.gitlab_token}@")
        
        logging.info(f"Pushing configuration from {local_path} to {http_url}...")
        if not os.path.exists(os.path.join(local_path, ".git")):
            self.run_git(["git", "init", "-b", "main"], local_path)
            
        self.run_git(["git", "config", "user.name", "Agent OS Deployer"], local_path)
        self.run_git(["git", "config", "user.email", "deployer@agent-os.arpa"], local_path)
        
        self.run_git(["git", "add", "."], local_path)
        self.run_git(["git", "commit", "-m", "chore: sync compose for GitOps deployment"], local_path)
        
        self.run_git(["git", "remote", "remove", "origin"], local_path)
        self.run_git(["git", "remote", "add", "origin", auth_url], local_path)
        
        if self.run_git(["git", "push", "-u", "origin", "main", "--force"], local_path):
            logging.info(f"Pushed service {service_name} successfully.")
            return http_url
        return False

    def deploy_portainer_gitops(self, service_name, repo_url, compose_path="docker-compose.yml"):
        logging.info(f"Querying active stacks to capture environment for {service_name}...")
        stacks_res = requests.get(f"{self.portainer_url}/api/stacks", headers=self.portainer_headers)
        if stacks_res.status_code != 200:
            logging.error(f"Failed to query stacks: {stacks_res.text}")
            return False
            
        stacks = stacks_res.json()
        target_stack = None
        for stack in stacks:
            if stack["Name"] == service_name:
                target_stack = stack
                break
                
        env_vars = []
        if target_stack:
            env_vars = target_stack.get("Env", [])
            stack_id = target_stack["Id"]
            logging.info(f"Stack {service_name} (ID: {stack_id}) exists. Rebuilding stack...")
            
            # Delete active stack
            del_res = requests.delete(f"{self.portainer_url}/api/stacks/{stack_id}?endpointId={self.endpoint_id}&external=false", headers=self.portainer_headers)
            if del_res.status_code not in [200, 204]:
                logging.error(f"Failed to delete stack: {del_res.text}")
                return False
            time.sleep(10)
            
        # Deploy Swarm GitOps stack
        swarm_stacks_url = f"{self.portainer_url}/api/stacks/create/swarm/repository?endpointId={self.endpoint_id}"
        payload = {
            "name": service_name,
            "repositoryURL": repo_url,
            "repositoryReferenceName": "refs/heads/main",
            "composeFilePathInRepository": compose_path,
            "additionalFiles": [],
            "repositoryAuthentication": True,
            "repositoryUsername": "oauth2",
            "repositoryPassword": self.gitlab_token,
            "env": env_vars,
            "autoUpdate": {
                "interval": "5m"
            }
        }
        deploy_res = requests.post(swarm_stacks_url, headers=self.portainer_headers, json=payload)
        if deploy_res.status_code == 200:
            logging.info(f"Successfully deployed GitOps Swarm stack: {service_name}")
            return True
        else:
            logging.error(f"Failed to deploy stack: {deploy_res.text}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Agent OS Scaled GitOps Synchronization Utility")
    parser.add_argument("--inventory", help="Path to Ansible inventory.yml/yaml")
    parser.add_argument("--workspace", help="Path to workspace.yml")
    parser.add_argument("--service-path", required=True, help="Local directory path containing service compose files")
    parser.add_argument("--service-name", required=True, help="Target service stack name")
    parser.add_argument("--gitlab-project", required=True, help="GitLab namespace project path, e.g. homelab/containers/services/twenty")
    parser.add_argument("--gitlab-url", required=True, help="GitLab URL")
    parser.add_argument("--gitlab-token", required=True, help="GitLab access token")
    parser.add_argument("--portainer-url", required=True, help="Portainer admin API URL")
    parser.add_argument("--portainer-token", required=True, help="Portainer API key")
    parser.add_argument("--endpoint-id", default="3", help="Portainer target Swarm/Docker endpoint ID")

    args = parser.parse_args()

    syncer = GitOpsSyncer(args.gitlab_url, args.gitlab_token, args.portainer_url, args.portainer_token, args.endpoint_id)

    # Trigger discovery scans if optional configurations are supplied
    if args.inventory:
        syncer.parse_inventory(args.inventory)
    if args.workspace:
        syncer.parse_workspace(args.workspace)

    repo_url = syncer.sync_to_gitlab(args.service_path, args.service_name, args.gitlab_project)
    if repo_url:
        syncer.deploy_portainer_gitops(args.service_name, repo_url)

if __name__ == "__main__":
    main()
