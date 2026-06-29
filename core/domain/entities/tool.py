from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum


class ToolCategory(str, Enum):
    GENERAL = "general"
    FINANCE = "finance"
    CHURCH = "church"
    WORKSHOP = "workshop"
    REAL_ESTATE = "real_estate"
    GLAZIER = "glazier"
    CUSTOM = "custom"


@dataclass
class ToolParameter:
    name: str
    type: str
    description: str = ""
    required: bool = False


@dataclass
class ToolDef:
    id: str
    app_id: str
    name: str
    description: str
    parameters: list[ToolParameter] = field(default_factory=list)
    category: ToolCategory = ToolCategory.GENERAL
    endpoint: str = ""
    method: str = "POST"
    headers: dict = field(default_factory=dict)
    is_active: bool = True

    def to_openai_schema(self) -> dict:
        properties = {}
        required = []
        for p in self.parameters:
            properties[p.name] = {"type": p.type, "description": p.description}
            if p.required:
                required.append(p.name)
        schema = {"type": "object", "properties": properties}
        if required:
            schema["required"] = required
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": schema,
            },
        }
