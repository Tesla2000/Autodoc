from __future__ import annotations

import traceback

from src.config import Config
from src.config import create_config_with_args
from src.config import parse_arguments
from src.transform.modify_code import modify_code


def main() -> int:
    args = parse_arguments(Config)
    config = create_config_with_args(Config, args)
    try:
        print(
            modify_code(
                config.code,
                config=config,
            )
        )
        return 0
    except Exception as e:
        print("Error: " + str(e))
        print("Traceback: " + traceback.format_exc())
        return 1


if __name__ == "__main__":
    exit(main())
