import argparse
import json
from pathlib import Path

from generate_dataset import OUT, generate


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a multi-week synthetic plant operations dataset.")
    parser.add_argument("--days", type=int, default=21)
    parser.add_argument("--seed", type=int, default=20261106)
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    print(json.dumps(generate(args.days, args.seed, args.output), indent=2))
