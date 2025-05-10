import argparse
from gx_init import GXInitiator

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize Great Expectations context.")
    parser.add_argument("--mode", choices=["recreate", "init"], default="init",
                        help="Specify whether to recreate the project directory or leave it as is.")
    args = parser.parse_args()

    GXInitiator.initialize(mode=args.mode)
