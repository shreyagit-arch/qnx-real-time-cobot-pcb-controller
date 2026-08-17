import csv
import os
from datetime import datetime


RESULTS_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "results",
    "raw"
)


def log_result(data):

    os.makedirs(RESULTS_DIR, exist_ok=True)

    experiment_name = data["experiment"]

    filename = os.path.join(
        RESULTS_DIR,
        f"{experiment_name}.csv"
    )

    fieldnames = [
        "timestamp",
        "experiment",
        "trial",
        "vision_workload",
        "ipc_workload",
        "control_workload",
        "vision_us",
        "ipc_us",
        "control_us",
        "end_to_end_us",
        "vision_status",
        "ipc_status",
        "control_status",
        "end_to_end_status",
        "fault",
        "robot_state",
        "safety_latch"
    ]

    file_exists = os.path.exists(filename)

    with open(
        filename,
        "a",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        if not file_exists:
            writer.writeheader()

        row = {
            "timestamp": datetime.now().isoformat(),
            **data
        }

        writer.writerow(row)

    print(
        f"RESULT SAVED : {filename}"
    )