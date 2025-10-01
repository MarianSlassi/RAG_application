import yaml
def load_project_config():
    with open("project_config.yaml", "r") as f:
        return yaml.safe_load(f)