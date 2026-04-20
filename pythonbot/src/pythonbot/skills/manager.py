from typing import Any
import yaml
from pathlib import Path
from pythonbot.core.config import DATA_DIR
from datetime import datetime

class SkillManager:
    def __init__(self):
        self.skills_dir = DATA_DIR / "skills"
        self.skills_dir.mkdir(parents=True, exist_ok=True)

    def create_skill(self, name: str, description: str, steps: list, tags: list) -> str:
        skill_data = {
            "name": name,
            "description": description,
            "steps": steps,
            "tags": tags,
            "created_at": str(datetime.now().date())
        }
        
        file_path = self.skills_dir / f"{name}.yaml"
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(skill_data, f, sort_keys=False, allow_unicode=True)
            
        return f"Skill '{name}' criada em {file_path}"

    def list_skills(self) -> list:
        skills = []
        for file in self.skills_dir.glob("*.yaml"):
            with open(file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data:
                    skills.append(data)
        return skills

    async def execute_skill(self, name: str, context_vars: dict = None) -> str:
        file_path = self.skills_dir / f"{name}.yaml"
        if not file_path.exists():
            return f"Skill '{name}' não encontrada."
            
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            
        from pythonbot.tools.registry import tool_registry
        
        output = []
        for i, step in enumerate(data.get("steps", [])):
            tool_name = step.get("tool")
            args = step.copy()
            del args["tool"] # remove tool key, rest are kwargs
            
            output.append(f"Executando Step {i+1}: {tool_name}")
            try:
                res = await tool_registry.execute_tool(tool_name, **args)
                output.append(f"Resultado: {str(res)[:100]}...\n")
            except Exception as e:
                output.append(f"Erro no step {i+1}: {e}\n")
                break # Para no erro
                
        return "\n".join(output)

skill_manager = SkillManager()
