import subprocess
import os

def run_module(module_name: str):
    module_path = os.path.abspath(f"modules/{module_name}")

    cmd = [
        "docker", "run",
        "--rm",
        "--memory=512m",
        "--cpus=0.5",
        "--network=none",
        "-v", f"{module_path}:/workspace:ro",
        "python:3.11-slim",
        "bash", "-c",
        "cd /workspace && pip install pytest -q && pytest -q"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr
