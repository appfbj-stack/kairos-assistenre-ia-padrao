from __future__ import annotations
from typing import Optional

from .models import AionSkill, ExecutionStatus, TaskResult


class AionSkillRegistry:
    def __init__(self):
        self._skills: dict[str, AionSkill] = {}

    def register(self, skill: AionSkill):
        self._skills[skill.name] = skill

    def register_batch(self, skills: list[AionSkill]):
        for s in skills:
            self.register(s)

    def get(self, name: str) -> Optional[AionSkill]:
        return self._skills.get(name)

    def list(self) -> list[AionSkill]:
        return list(self._skills.values())

    def list_active(self) -> list[AionSkill]:
        return [s for s in self._skills.values() if s.is_active]

    def list_by_category(self, category: str) -> list[AionSkill]:
        return [s for s in self._skills.values() if s.category == category and s.is_active]

    def activate(self, name: str) -> bool:
        skill = self._skills.get(name)
        if skill:
            skill.is_active = True
            return True
        return False

    def deactivate(self, name: str) -> bool:
        skill = self._skills.get(name)
        if skill:
            skill.is_active = False
            return True
        return False

    def to_openai_tools(self) -> list[dict]:
        tools = []
        for skill in self.list_active():
            properties = {}
            required = []
            for p in skill.parameters:
                properties[p["name"]] = {
                    "type": p.get("type", "string"),
                    "description": p.get("description", ""),
                }
                if p.get("required", False):
                    required.append(p["name"])
            schema = {"type": "object", "properties": properties}
            if required:
                schema["required"] = required
            tools.append({
                "type": "function",
                "function": {
                    "name": f"aion_{skill.name}",
                    "description": f"[Aion Skill] {skill.description}",
                    "parameters": schema,
                },
            })
        return tools

    def count(self) -> int:
        return len(self._skills)
