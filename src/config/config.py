import pathlib
import yaml


PROJECT_PATH = pathlib.Path(__file__).parent.parent.parent

DB_PATH = PROJECT_PATH / "storage" / "database" / "database.db"
YAML_PATH = PROJECT_PATH / "config.yaml"

with open(YAML_PATH) as f:
    CONFIG = yaml.safe_load(f)
