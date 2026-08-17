import time


IPC_DEADLINE_US = 5000


def send_message(message, workload="NORMAL", config=None):

    if config is not None:
        delay_us = config["workload_delays_us"]["ipc"][workload]
    else:
        delay_us = 1000

    start = time.perf_counter_ns()

    time.sleep(delay_us / 1_000_000)

    end = time.perf_counter_ns()

    elapsed_us = (end - start) / 1000

    status = elapsed_us <= IPC_DEADLINE_US

    print(
        f"IPC TIMING : {elapsed_us:.0f} us | "
        f"DEADLINE = {IPC_DEADLINE_US} us | "
        f"{'MET' if status else 'MISS'}"
    )

    print(
        f"IPC : MESSAGE SENT -> {message}"
    )

    return message, status