import argparse
import subprocess
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent

STEPS = {
    "schema": ["extract_schema.py"],
    "architect": ["llama_architect.py"],
    "monitor": ["ml_engine.py", "--monitor"],
    "scan": ["ml_engine.py", "--once"],
    "api": ["ml_engine.py", "--api"],
}


def run_step(name):
    command = [sys.executable, *STEPS[name]]
    print(f"\n==> Running {name}: {' '.join(command)}")
    subprocess.run(command, check=True, cwd=BACKEND_DIR)


def main():
    parser = argparse.ArgumentParser(description="Run the Tulip 2.0 anomaly architecture steps.")
    parser.add_argument(
        "step",
        choices=["schema", "architect", "monitor", "scan", "api", "bootstrap"],
        help="Use bootstrap for schema then architect. Use monitor/api for the runtime service. Use scan for one manual scan.",
    )
    args = parser.parse_args()

    if args.step == "bootstrap":
        run_step("schema")
        run_step("architect")
        return

    run_step(args.step)


if __name__ == "__main__":
    main()
