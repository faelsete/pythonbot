from pythonbot.doctor.diagnostics import doctor_diagnostics

class DoctorReporter:
    def generate_report(self):
        res = doctor_diagnostics.check_all()
        lines = ["[Doctor Report]"]
        for k, v in res.items():
            icon = "✅" if v["status"] == "ok" else "❌" if v["status"] == "error" else "⚠️"
            lines.append(f"{icon} {k.upper()}: {v['msg']}")
        return "\n".join(lines)

doctor_reporter = DoctorReporter()
