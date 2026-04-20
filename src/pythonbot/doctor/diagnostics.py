import sys
import platform
import shutil


class DoctorDiagnostics:
    def check_all(self) -> dict:
        results = {}

        # 1. Python version
        results["python"] = {
            "status": "ok" if sys.version_info >= (3, 11) else "error",
            "msg": f"Python {sys.version.split()[0]}"
        }

        # 2. System binaries
        results["ffmpeg"] = {
            "status": "ok" if shutil.which("ffmpeg") else "warning",
            "msg": "ffmpeg" + (" disponível" if shutil.which("ffmpeg") else " ausente (TTS/STT limitados)")
        }
        results["npx"] = {
            "status": "ok" if shutil.which("npx") else "warning",
            "msg": "Node.js (npx)" + (" disponível" if shutil.which("npx") else " ausente (MCPs indisponíveis)")
        }

        # 3. Critical libraries
        for lib_name, pkg_name in [("mcp", "mcp[cli]"), ("fastapi", "fastapi")]:
            try:
                __import__(lib_name)
                results[lib_name] = {"status": "ok", "msg": f"{pkg_name} instalado"}
            except ImportError:
                results[lib_name] = {"status": "error", "msg": f"{pkg_name} faltando"}

        # 4. Disk space (using shutil — psutil has issues on Python 3.13/Windows)
        try:
            disk_path = "C:\\" if platform.system() == "Windows" else "/"
            disk = shutil.disk_usage(disk_path)
            free_gb = disk.free // (1024**3)
            results["disk"] = {
                "status": "ok" if free_gb > 1 else "warning",
                "msg": f"Espaço livre: {free_gb}GB"
            }
        except Exception as e:
            results["disk"] = {"status": "warning", "msg": f"Não foi possível verificar disco: {e}"}

        # 5. LLM Provider
        try:
            from pythonbot.core.config import settings
            if settings.llm_api_key:
                results["llm"] = {"status": "ok", "msg": f"Provider: {settings.llm_provider} ({settings.llm_model})"}
            else:
                results["llm"] = {"status": "warning", "msg": "API Key LLM não configurada"}
        except Exception:
            results["llm"] = {"status": "error", "msg": "Não foi possível carregar config LLM"}

        return results


doctor_diagnostics = DoctorDiagnostics()
