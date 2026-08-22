import json
import os
import time
import csv

from vision import run_vision
from ipc import send_message
from control import run_control
from robot import Robot
from fault_manager import FaultManager
from safety_manager import SafetyManager


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_FILE = os.path.join(
    BASE_DIR,
    "config",
    "experiment_config.json"
)


def load_config():

    with open(CONFIG_FILE, "r") as file:
        return json.load(file)


config = load_config()


# ============================================================
# CONFIG VALUES
# ============================================================

VISION_DEADLINE = config["deadlines"]["vision_us"]
IPC_DEADLINE = config["deadlines"]["ipc_us"]
CONTROL_DEADLINE = config["deadlines"]["control_us"]
E2E_DEADLINE = config["deadlines"]["end_to_end_us"]

VISION_WORKLOAD = config["workload"]["vision"]
IPC_WORKLOAD = config["workload"]["ipc"]
CONTROL_WORKLOAD = config["workload"]["control"]

EXPERIMENT_NAME = config["experiment"]["name"]
TRIALS = config["experiment"]["trials"]

FAULT_ENABLED = config["fault_injection"]["enabled"]
FAULT_TYPE = config["fault_injection"]["type"]
FAULT_DELAY = config["fault_injection"]["delay_us"]


# ============================================================
# RESULT DIRECTORY
# ============================================================

RESULTS_DIR = os.path.join(
    BASE_DIR,
    "results",
    "raw"
)

os.makedirs(
    RESULTS_DIR,
    exist_ok=True
)


# ============================================================
# ROBOT / FAULT / SAFETY
# ============================================================

robot = Robot()

fault_manager = FaultManager()

safety_manager = SafetyManager()


# ============================================================
# SINGLE EXPERIMENT RUN
# ============================================================

def run_experiment(trial_number=1):

    print("\n================================")
    print(" QNX PCB COBOT RESEARCH SIMULATOR")
    print("================================\n")

    start_e2e = time.perf_counter_ns()

    print("SYSTEM : STARTING")

    # --------------------------------------------------------
    # INITIAL ROBOT STATE
    # --------------------------------------------------------

    print(
        f"ROBOT : INITIAL STATE = {robot.state}"
    )


    # ========================================================
    # VISION
    # ========================================================

    print(
        f"VISION WORKLOAD : {VISION_WORKLOAD}"
    )

    vision_start = time.perf_counter_ns()

    vision_result = run_vision(
        workload=VISION_WORKLOAD,
        config=config
    )

    vision_end = time.perf_counter_ns()

    vision_time_us = (
        vision_end - vision_start
    ) / 1000

    vision_status = (
        vision_time_us <= VISION_DEADLINE
    )

    print(
        f"VISION TIMING : {vision_time_us:.0f} us | "
        f"DEADLINE = {VISION_DEADLINE} us | "
        f"{'MET' if vision_status else 'MISS'}"
    )

    print(
        f"VISION : {vision_result}"
    )


    # ========================================================
    # INSPECTION FAILURE HANDLING
    # ========================================================

    if vision_result != "PASS":

        fault_manager.report_fault(
            "INSPECTION_FAILURE"
        )

        safety_manager.request_stop(
            robot
        )

        end_e2e = time.perf_counter_ns()

        e2e_time_us = (
            end_e2e - start_e2e
        ) / 1000

        e2e_status = (
            e2e_time_us <= E2E_DEADLINE
        )

        print(
            "INSPECTION FAILURE : "
            "ROBOT STOP REQUESTED"
        )

        print(
            f"END-TO-END TIMING : "
            f"{e2e_time_us:.0f} us | "
            f"DEADLINE = {E2E_DEADLINE} us | "
            f"{'MET' if e2e_status else 'MISS'}"
        )

        print(
            f"ROBOT : FINAL STATE = "
            f"{robot.state}"
        )

        return {
            "experiment": EXPERIMENT_NAME,
            "trial": trial_number,

            "vision_us":
                round(vision_time_us),

            "ipc_us": 0,

            "control_us": 0,

            "end_to_end_us":
                round(e2e_time_us),

            "vision_deadline_miss":
                int(not vision_status),

            "ipc_deadline_miss": 0,

            "control_deadline_miss": 0,

            "end_to_end_deadline_miss":
                int(not e2e_status),

            "robot_state":
                robot.state
        }


    # ========================================================
    # VISION DEADLINE FAULT
    # ========================================================

    if not vision_status:

        fault_manager.report_fault(
            "VISION_DEADLINE_VIOLATION"
        )

        safety_manager.request_stop(
            robot
        )

        end_e2e = time.perf_counter_ns()

        e2e_time_us = (
            end_e2e - start_e2e
        ) / 1000

        e2e_status = (
            e2e_time_us <= E2E_DEADLINE
        )

        print(
            f"\nEND-TO-END TIMING : "
            f"{e2e_time_us:.0f} us | "
            f"DEADLINE = {E2E_DEADLINE} us | "
            f"{'MET' if e2e_status else 'MISS'}"
        )

        print(
            f"\nROBOT : FINAL STATE = "
            f"{robot.state}"
        )

        return {
            "experiment": EXPERIMENT_NAME,
            "trial": trial_number,

            "vision_us":
                round(vision_time_us),

            "ipc_us": 0,

            "control_us": 0,

            "end_to_end_us":
                round(e2e_time_us),

            "vision_deadline_miss":
                int(not vision_status),

            "ipc_deadline_miss": 0,

            "control_deadline_miss": 0,

            "end_to_end_deadline_miss":
                int(not e2e_status),

            "robot_state":
                robot.state
        }


    # ========================================================
    # IPC
    # ========================================================

    print(
        f"IPC WORKLOAD : {IPC_WORKLOAD}"
    )

    ipc_start = time.perf_counter_ns()

    message, ipc_status = send_message(
        vision_result,
        workload=IPC_WORKLOAD,
        config=config
    )

    ipc_end = time.perf_counter_ns()

    ipc_time_us = (
        ipc_end - ipc_start
    ) / 1000

    ipc_status = (
        ipc_time_us <= IPC_DEADLINE
    )

    print(
        f"IPC TIMING : {ipc_time_us:.0f} us | "
        f"DEADLINE = {IPC_DEADLINE} us | "
        f"{'MET' if ipc_status else 'MISS'}"
    )


    # ========================================================
    # IPC DEADLINE FAULT
    # ========================================================

    if not ipc_status:

        fault_manager.report_fault(
            "IPC_DEADLINE_VIOLATION"
        )

        safety_manager.request_stop(
            robot
        )

        end_e2e = time.perf_counter_ns()

        e2e_time_us = (
            end_e2e - start_e2e
        ) / 1000

        e2e_status = (
            e2e_time_us <= E2E_DEADLINE
        )

        print(
            f"\nEND-TO-END TIMING : "
            f"{e2e_time_us:.0f} us | "
            f"DEADLINE = {E2E_DEADLINE} us | "
            f"{'MET' if e2e_status else 'MISS'}"
        )

        print(
            f"\nROBOT : FINAL STATE = "
            f"{robot.state}"
        )

        return {
            "experiment": EXPERIMENT_NAME,
            "trial": trial_number,

            "vision_us":
                round(vision_time_us),

            "ipc_us":
                round(ipc_time_us),

            "control_us": 0,

            "end_to_end_us":
                round(e2e_time_us),

            "vision_deadline_miss":
                int(not vision_status),

            "ipc_deadline_miss":
                int(not ipc_status),

            "control_deadline_miss": 0,

            "end_to_end_deadline_miss":
                int(not e2e_status),

            "robot_state":
                robot.state
        }


    print(
        f"IPC : MESSAGE SENT -> {message}"
    )


    # ========================================================
    # CONTROL
    # ========================================================

    print("CONTROL: ACTIVE")

    print(
        f"CONTROL WORKLOAD : "
        f"{CONTROL_WORKLOAD}"
    )

    control_start = time.perf_counter_ns()


    # ========================================================
    # CONTROL FAULT INJECTION
    # ========================================================

    if (
        FAULT_ENABLED
        and FAULT_TYPE == "CONTROL_DELAY"
    ):

        print(
            f"FAULT INJECTION : "
            f"CONTROL +{FAULT_DELAY} us"
        )

        time.sleep(
            FAULT_DELAY / 1_000_000
        )


    # ========================================================
    # RUN CONTROL
    # ========================================================

    control_result = run_control(
        message,
        workload=CONTROL_WORKLOAD,
        config=config,
        robot=robot
    )

    control_end = time.perf_counter_ns()

    control_time_us = (
        control_end - control_start
    ) / 1000

    control_status = (
        control_time_us <= CONTROL_DEADLINE
    )

    print(
        f"TIMING : CONTROL = "
        f"{control_time_us:.0f} us | "
        f"DEADLINE = {CONTROL_DEADLINE} us | "
        f"{'MET' if control_status else 'MISS'}"
    )


    # ========================================================
    # CONTROL DEADLINE FAULT
    # ========================================================

    if not control_status:

        fault_manager.report_fault(
            "CONTROL_DEADLINE_VIOLATION"
        )

        safety_manager.request_stop(
            robot
        )


    # ========================================================
    # END-TO-END TIMING
    # ========================================================

    end_e2e = time.perf_counter_ns()

    e2e_time_us = (
        end_e2e - start_e2e
    ) / 1000

    e2e_status = (
        e2e_time_us <= E2E_DEADLINE
    )

    print(
        f"\nEND-TO-END TIMING : "
        f"{e2e_time_us:.0f} us | "
        f"DEADLINE = {E2E_DEADLINE} us | "
        f"{'MET' if e2e_status else 'MISS'}"
    )


    # ========================================================
    # END-TO-END DEADLINE FAULT
    # ========================================================

    if not e2e_status:

        fault_manager.report_fault(
            "END_TO_END_DEADLINE_VIOLATION"
        )

        safety_manager.request_stop(
            robot
        )


    # ========================================================
    # FINAL STATE
    # ========================================================

    print(
        f"\nROBOT : FINAL STATE = "
        f"{robot.state}"
    )


    # ========================================================
    # RETURN RESULT
    # ========================================================

    return {
        "experiment": EXPERIMENT_NAME,
        "trial": trial_number,

        "vision_us":
            round(vision_time_us),

        "ipc_us":
            round(ipc_time_us),

        "control_us":
            round(control_time_us),

        "end_to_end_us":
            round(e2e_time_us),

        "vision_deadline_miss":
            int(not vision_status),

        "ipc_deadline_miss":
            int(not ipc_status),

        "control_deadline_miss":
            int(not control_status),

        "end_to_end_deadline_miss":
            int(not e2e_status),

        "robot_state":
            robot.state
    }


# ============================================================
# CSV LOGGER
# ============================================================

def save_results(results):

    filename = (
        f"{EXPERIMENT_NAME}.csv"
    )

    filepath = os.path.join(
        RESULTS_DIR,
        filename
    )

    file_exists = os.path.exists(
        filepath
    )

    fieldnames = [
        "experiment",
        "trial",
        "vision_us",
        "ipc_us",
        "control_us",
        "end_to_end_us",
        "vision_deadline_miss",
        "ipc_deadline_miss",
        "control_deadline_miss",
        "end_to_end_deadline_miss",
        "robot_state"
    ]

    with open(
        filepath,
        "a",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        if not file_exists:

            writer.writeheader()

        writer.writerow(
            results
        )

    print(
        f"RESULT SAVED : {filepath}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # RESET ROBOT
    # --------------------------------------------------------

    robot.state = "READY"
    robot.safety_latch = False


    # --------------------------------------------------------
    # AUTOMATED EXPERIMENT
    # --------------------------------------------------------

    if TRIALS > 1:

        print(
            "\n############################################"
        )

        print(
            " AUTOMATED EXPERIMENT"
        )

        print(
            "############################################"
        )

        print(
            f"EXPERIMENT : {EXPERIMENT_NAME}"
        )

        print(
            f"TRIALS     : {TRIALS}"
        )


        # ----------------------------------------------------
        # TRIAL LOOP
        # ----------------------------------------------------

        for trial in range(
            1,
            TRIALS + 1
        ):

            print(
                "\n================================"
            )

            print(
                f"EXPERIMENT : "
                f"{EXPERIMENT_NAME}"
            )

            print(
                f"TRIAL      : {trial}"
            )


            # ------------------------------------------------
            # RESET ROBOT BEFORE EACH TRIAL
            # ------------------------------------------------

            robot.state = "READY"

            robot.safety_latch = False


            # ------------------------------------------------
            # RESET FAULT MANAGER
            # ------------------------------------------------

            fault_manager.fault_active = False
            fault_manager.fault_type = None


            # ------------------------------------------------
            # RESET SAFETY MANAGER
            # ------------------------------------------------

            safety_manager.state = "NORMAL"
            safety_manager.safety_latch = False


            # ------------------------------------------------
            # RUN EXPERIMENT
            # ------------------------------------------------

            result = run_experiment(
                trial
            )


            # ------------------------------------------------
            # SAVE RESULT
            # ------------------------------------------------

            save_results(
                result
            )


            print(
                f"\nTRIAL {trial} COMPLETE"
            )


        # ----------------------------------------------------
        # ALL TRIALS COMPLETE
        # ----------------------------------------------------

        print(
            "\n############################################"
        )

        print(
            " ALL TRIALS COMPLETE"
        )

        print(
            "############################################"
        )

        print(
            f"TOTAL TRIALS : {TRIALS}"
        )

        print(
            "\nEXPERIMENT COMPLETE"
        )


    # --------------------------------------------------------
    # SINGLE TRIAL
    # --------------------------------------------------------

    else:

        result = run_experiment(
            1
        )

        save_results(
            result
        )

        print(
            "\nSIMULATION COMPLETE"
        )