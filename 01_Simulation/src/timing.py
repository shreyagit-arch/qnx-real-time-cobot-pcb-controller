import time

from config import load_config


def measure_execution(name, function, deadline_us):

    config = load_config()

    workload = config["workload"]["control"]

    delay_us = config["workload_delays_us"]["control"][workload]

    fault = config["fault_injection"]

    print(
        f"CONTROL WORKLOAD : {workload}"
    )

    start = time.perf_counter_ns()

    if (
        fault["enabled"]
        and fault["type"] == "CONTROL_DELAY"
    ):

        print(
            f"FAULT INJECTION : "
            f"CONTROL +{fault['delay_us']} us"
        )

        time.sleep(
            fault["delay_us"] / 1_000_000
        )

    if delay_us > 0:

        time.sleep(
            delay_us / 1_000_000
        )

    function()

    end = time.perf_counter_ns()

    execution_us = (end - start) / 1_000

    deadline_met = execution_us <= deadline_us

    status = "MET" if deadline_met else "MISS"

    print(
        f"TIMING : {name} = "
        f"{execution_us:.0f} us | "
        f"DEADLINE = {deadline_us} us | "
        f"{status}"
    )

    return execution_us, deadline_met