import re
import yaml
from typing import Dict, Any, List

class RuleMatch:
    def __init__(self, rule_id: str, name: str, severity: str, description: str):
        self.rule_id = rule_id
        self.name = name
        self.severity = severity
        self.description = description

    def to_dict(self):
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "severity": self.severity,
            "description": self.description
        }

class RuleEngine:
    def __init__(self, rules_path: str = "rules.yaml"):
        self.rules = []
        self.load_rules(rules_path)

    #! simple load
    def load_rules(self, rules_path: str):
        with open(rules_path, "r") as f:
            config = yaml.safe_load(f)

        self.rules = []
        for rule in config.get("rules", []):
            self.rules.append({
                "id": rule["id"],
                "name": rule["name"],
                "severity": rule["severity"],
                "target_field": rule["target_field"],
                "description": rule["description"],
                #! expresion transfer
                "compiled_regex": re.compile(rule["pattern"])
            })
        print(f"[RuleEngine]: Loaded {len(self.rules)} deterministic rules.")

    #! Takes log runs all rules and see of it contains any of the signtures
    def evaluate(self, log: Dict[str, Any]) -> List[RuleMatch]:
        matches = []

        for rule in self.rules:
            field_value = str(log.get(rule["target_field"], ""))

            if field_value and rule["compiled_regex"].search(field_value):
                matches.append(RuleMatch(
                    rule_id=rule["id"],
                    name=rule["name"],
                    severity=rule["severity"],
                    description=rule["description"]
                ))

        return matches