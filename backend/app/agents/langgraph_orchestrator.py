————processada pelo sistema Aion."
        )

        return {
            "task_id": task_id,
            "success": exec_result.get("success", True),
            "response": response_text,
            "plan": plan,
            "execution": exec_result,
            "qa": qa_result,
            "automation": state.get("automation_result"),
            "app_context": state.get("app_context"),
            "skills_used": state.get("skills_used", []),
            "errors": state.get("errors", []),
            "iterations": state.get("iteration_count", 0),
            "agents_used": ["planner", "executor", "qa"]
                           + (["automation"] if state.get("automation_result") else []),
        }

    def get_app_registry(self) -> list:
        return self.app_integration.list_apps()
