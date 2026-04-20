from pythonbot.doctor.diagnostics import doctor_diagnostics

class DoctorRepair:
    def auto_repair(self):
        issues = doctor_diagnostics.check_all()
        fixes = []
        
        for key, val in issues.items():
            if val["status"] == "error":
                # Lógica heurística simplificada
                if key == "mcp":
                    fixes.append("uv add mcp[cli]")
                elif key == "fastapi":
                    fixes.append("uv add fastapi uvicorn")
                elif key == "ffmpeg":
                    fixes.append("sudo apt install ffmpeg (ou choco install ffmpeg)")
                    
        return fixes

doctor_repair = DoctorRepair()
