import time

CONTROL_DEADLINE_US = 80000


def run_control(message, workload="NORMAL", config=None, robot=None):

    if config is not None:
        delay_us = config["workload_delays_us"]["control"][workload]
    else:
        delay_us = 0

    start = time.perf_counter_ns()

    if delay_us > 0:
        time.sleep(delay_us / 1_000_000)

    if robot is not None and message == "PASS":

        robot.pick()
        robot.move()
        robot.place()

        # Return robot to ready state after successful cycle
        if hasattr(robot, "ready"):
            robot.ready()

    end = time.perf_counter_ns()

    elapsed_us = (end - start) / 1000

    return elapsed_us