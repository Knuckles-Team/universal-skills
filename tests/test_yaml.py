import os
import yaml

def check_skills():
    skills_dir = "universal_skills/skills"
    errors = 0
    for root, _, files in os.walk(skills_dir):
        if "SKILL.md" in files:
            path = os.path.join(root, "SKILL.md")
            with open(path, "r") as f:
                content = f.read()
            if content.startswith("---"):
                end_idx = content.find("---", 3)
                if end_idx != -1:
                    yaml_content = content[3:end_idx]
                    try:
                        parsed = yaml.safe_load(yaml_content)
                        if 'name' not in parsed or 'description' not in parsed:
                            print(f"{path} missing 'name' or 'description'")
                            errors += 1
                    except Exception as e:
                        print(f"Error parsing {path}: {e}")
                        errors += 1
                else:
                    print(f"{path} missing closing --- block")
                    errors += 1
            else:
                print(f"{path} missing starting --- block")
                errors += 1


    if errors == 0:
        print("All SKILL.md files parsed successfully.")
    else:
        print(f"Total errors: {errors}")

if __name__ == "__main__":
    check_skills()
