import sys
import os

# Projekt-Root zum sys.path hinzufügen
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import yaml
from modules.registry import ANALYSIS_MODULES

def validate_industry_profiles(path="config/industry_profiles.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        profiles = yaml.safe_load(f)

    all_valid_keys = set(ANALYSIS_MODULES.keys())
    errors = {}

    for industry, settings in profiles.items():
        requested_modules = settings.get("modules", [])
        invalid = [m for m in requested_modules if m not in all_valid_keys]
        if invalid:
            errors[industry] = invalid

    if errors:
        print("Fehlerhafte Module in YAML-Profilen:")
        for industry, invalid_mods in errors.items():
            print(f"- {industry}: {invalid_mods}")
    else:
        print("Alle Module in den YAML-Profilen sind gültig.")

if __name__ == "__main__":
    validate_industry_profiles()
