import yaml

def get_modules_for_industry(industry: str, config_path="config/industry_profiles.yaml") -> list:
    try:
        with open(config_path, "r") as f:
            profiles = yaml.safe_load(f)
        modules = profiles.get(industry, {}).get("modules", [])
        # insights immer anhängen, falls nicht drin
        if "insights" not in modules:
            modules.append("insights")
        return modules
    except Exception:
        return ["insights"]



