import time

from timing import measure_execution


def control_task():
    time.sleep(0.05)


measure_execution(
    "CONTROL",
    control_task,
    80_000
)