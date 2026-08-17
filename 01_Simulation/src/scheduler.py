from config import load_config


def load_priorities():

    config = load_config()

    priorities = config["priority"]

    print()
    print("SCHEDULER : PRIORITY CONFIGURATION")

    print(
        f"VISION  : PRIORITY = {priorities['vision']}"
    )

    print(
        f"IPC     : PRIORITY = {priorities['ipc']}"
    )

    print(
        f"CONTROL : PRIORITY = {priorities['control']}"
    )

    highest_task = max(
        priorities,
        key=priorities.get
    )

    print(
        f"SCHEDULER : HIGHEST PRIORITY = "
        f"{highest_task.upper()}"
    )

    return priorities