import yaml

CONFIG_PATH = "config/industry_profiles.yaml"

def get_industry_config(industry: str) -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        all_configs = yaml.safe_load(f)

    return all_configs.get(industry.lower(), all_configs["default"])
