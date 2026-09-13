import argparse
from pathlib import Path
from analyzer import analyze
from webserver import make_handler, serve


def process(payload):
    return analyze(payload.get("resume"), payload.get("job"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Local resume skill evidence explorer")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    serve(make_handler(process, Path(__file__).parent / "static"), args.port)
