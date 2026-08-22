import time


VISION_DEADLINE_US = 50000


def run_vision(workload="NORMAL", config=None):

    if config is not None:
        delay_us = config["workload_delays_us"]["vision"][workload]
    else:
        delay_us = 20000

    start = time.perf_counter_ns()

    time.sleep(delay_us / 1_000_000)

    end = time.perf_counter_ns()

    elapsed_us = (end - start) / 1000

    return config.get("inspection", {}).get("result", "PASS")
