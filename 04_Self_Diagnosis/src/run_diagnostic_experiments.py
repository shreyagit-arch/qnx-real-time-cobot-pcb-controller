"""
EdgeGuard Automated Diagnostic Experiment Runner

Runs controlled software-injected experiments for:
1. Normal operation
2. Thermal anomaly
3. Sensor noise/degradation
4. Power anomaly
5. Communication failure
6. Timing fault

Outputs raw experimental evidence to CSV.

IMPORTANT:
These are software-injected diagnostic experiments.
They are NOT physical sensor measurements.
"""

import csv
import os
import time
from datetime import datetime

from health_engine import HealthEngine
from response_manager import ResponseManager


TRIALS_PER_EXPERIMENT = 10


# ---------------------------------------------------------
# EXPERIMENT DEFINITIONS
# ---------------------------------------------------------

EXPERIMENTS = [
    {
        "id": "D01_NORMAL",
        "fault_domain": "NONE",
        "temperature_c": 42.0,
        "sensor_noise": 3.0,
        "power_deviation_percent": 4.0,
        "communication_errors": 0,
        "control_execution_us": 45_000,
        "expected_status": "HEALTHY",
        "expected_action": "LOG",
        "expected_system_state": "NORMAL",
    },

    {
        "id": "D02_THERMAL_FAULT",
        "fault_domain": "THERMAL",
        "temperature_c": 82.0,
        "sensor_noise": 3.0,
        "power_deviation_percent": 4.0,
        "communication_errors": 0,
        "control_execution_us": 45_000,
        "expected_status": "FAULT",
        "expected_action": "SAFE_MODE",
        "expected_system_state": "SAFE_MODE",
    },

    {
        "id": "D03_SENSOR_NOISE",
        "fault_domain": "SENSOR",
        "temperature_c": 42.0,
        "sensor_noise": 18.0,
        "power_deviation_percent": 4.0,
        "communication_errors": 0,
        "control_execution_us": 45_000,
        "expected_status": "FAULT",
        "expected_action": "DEGRADE",
        "expected_system_state": "DEGRADED",
    },

    {
        "id": "D04_POWER_ANOMALY",
        "fault_domain": "POWER",
        "temperature_c": 42.0,
        "sensor_noise": 3.0,
        "power_deviation_percent": 27.0,
        "communication_errors": 0,
        "control_execution_us": 45_000,
        "expected_status": "FAULT",
        "expected_action": "SAFE_MODE",
        "expected_system_state": "SAFE_MODE",
    },

    {
        "id": "D05_COMM_FAILURE",
        "fault_domain": "COMMUNICATION",
        "temperature_c": 42.0,
        "sensor_noise": 3.0,
        "power_deviation_percent": 4.0,
        "communication_errors": 5,
        "control_execution_us": 45_000,
        "expected_status": "FAULT",
        "expected_action": "SAFE_MODE",
        "expected_system_state": "SAFE_MODE",
    },

    {
        "id": "D06_TIMING_FAULT",
        "fault_domain": "TIMING",
        "temperature_c": 42.0,
        "sensor_noise": 3.0,
        "power_deviation_percent": 4.0,
        "communication_errors": 0,
        "control_execution_us": 100_000,
        "expected_status": "FAULT",
        "expected_action": "SAFE_MODE",
        "expected_system_state": "SAFE_MODE",
    },
]


# ---------------------------------------------------------
# OUTPUT PATH
# ---------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

RESULTS_DIR = os.path.abspath(
    os.path.join(
        SCRIPT_DIR,
        "..",
        "results"
    )
)

os.makedirs(
    RESULTS_DIR,
    exist_ok=True
)

RAW_OUTPUT_FILE = os.path.join(
    RESULTS_DIR,
    "diagnostic_experiments_raw.csv"
)


# ---------------------------------------------------------
# FIND TARGET RESULT
# ---------------------------------------------------------

def find_target_result(results, fault_domain):

    if fault_domain == "NONE":

        # For the normal experiment, verify that every
        # diagnostic domain remains healthy.

        return None

    for result in results:

        if result.domain == fault_domain:
            return result

    return None


# ---------------------------------------------------------
# RUN SINGLE TRIAL
# ---------------------------------------------------------

def run_trial(experiment, trial_number):

    engine = HealthEngine()
    manager = ResponseManager()

    start_ns = time.perf_counter_ns()

    results = engine.evaluate_system(
        temperature_c=experiment["temperature_c"],
        sensor_noise=experiment["sensor_noise"],
        power_deviation_percent=experiment[
            "power_deviation_percent"
        ],
        communication_errors=experiment[
            "communication_errors"
        ],
        control_execution_us=experiment[
            "control_execution_us"
        ],
    )

    manager.evaluate(results)

    end_ns = time.perf_counter_ns()

    diagnostic_latency_us = (
        end_ns - start_ns
    ) / 1000.0


    # -----------------------------------------------------
    # NORMAL EXPERIMENT
    # -----------------------------------------------------

    if experiment["fault_domain"] == "NONE":

        all_healthy = all(
            result.status == "HEALTHY"
            for result in results
        )

        all_log = all(
            result.action.value == "LOG"
            for result in results
        )

        observed_status = (
            "HEALTHY"
            if all_healthy
            else "UNEXPECTED"
        )

        observed_action = (
            "LOG"
            if all_log
            else "UNEXPECTED"
        )

        observed_score = max(
            result.diagnostic_score
            for result in results
        )

        detection_correct = (
            all_healthy
            and all_log
            and manager.state.value
            == experiment["expected_system_state"]
        )


    # -----------------------------------------------------
    # FAULT EXPERIMENT
    # -----------------------------------------------------

    else:

        target = find_target_result(
            results,
            experiment["fault_domain"]
        )

        if target is None:

            observed_status = "NOT_FOUND"
            observed_action = "NOT_FOUND"
            observed_score = -1.0

            detection_correct = False

        else:

            observed_status = target.status
            observed_action = target.action.value
            observed_score = target.diagnostic_score

            detection_correct = (
                observed_status
                == experiment["expected_status"]
                and observed_action
                == experiment["expected_action"]
                and manager.state.value
                == experiment["expected_system_state"]
            )


    # -----------------------------------------------------
    # COMMAND BLOCKING CHECK
    # -----------------------------------------------------

    pick_allowed = manager.command_allowed(
        "PICK"
    )

    move_allowed = manager.command_allowed(
        "MOVE"
    )

    place_allowed = manager.command_allowed(
        "PLACE"
    )


    return {
        "timestamp":
            datetime.now().isoformat(
                timespec="milliseconds"
            ),

        "experiment_id":
            experiment["id"],

        "trial":
            trial_number,

        "injected_fault_domain":
            experiment["fault_domain"],

        "temperature_c":
            experiment["temperature_c"],

        "sensor_noise":
            experiment["sensor_noise"],

        "power_deviation_percent":
            experiment[
                "power_deviation_percent"
            ],

        "communication_errors":
            experiment[
                "communication_errors"
            ],

        "control_execution_us":
            experiment[
                "control_execution_us"
            ],

        "expected_status":
            experiment["expected_status"],

        "observed_status":
            observed_status,

        "expected_action":
            experiment["expected_action"],

        "observed_action":
            observed_action,

        "expected_system_state":
            experiment[
                "expected_system_state"
            ],

        "observed_system_state":
            manager.state.value,

        "safe_mode_latched":
            manager.safe_mode_latched,

        "pick_allowed":
            pick_allowed,

        "move_allowed":
            move_allowed,

        "place_allowed":
            place_allowed,

        "diagnostic_score":
            round(
                observed_score,
                3
            ),

        "diagnostic_latency_us":
            round(
                diagnostic_latency_us,
                3
            ),

        "detection_correct":
            detection_correct,

        "result":
            "PASS"
            if detection_correct
            else "FAIL",
    }


# ---------------------------------------------------------
# MAIN EXPERIMENT RUNNER
# ---------------------------------------------------------

def main():

    rows = []

    print()
    print("=" * 72)
    print("EDGEGUARD AUTOMATED DIAGNOSTIC EXPERIMENTS")
    print("=" * 72)

    print(
        "Experiments:",
        len(EXPERIMENTS)
    )

    print(
        "Trials per experiment:",
        TRIALS_PER_EXPERIMENT
    )

    print(
        "Total trials:",
        len(EXPERIMENTS)
        * TRIALS_PER_EXPERIMENT
    )

    print("=" * 72)


    for experiment in EXPERIMENTS:

        print()
        print(
            "RUNNING:",
            experiment["id"]
        )

        passed = 0

        for trial in range(
            1,
            TRIALS_PER_EXPERIMENT + 1
        ):

            row = run_trial(
                experiment,
                trial
            )

            rows.append(row)

            if row["detection_correct"]:
                passed += 1

            print(
                f"  Trial {trial:02d} "
                f"-> {row['result']} "
                f"| State="
                f"{row['observed_system_state']} "
                f"| Latency="
                f"{row['diagnostic_latency_us']} us"
            )

        print(
            f"  RESULT: "
            f"{passed}/"
            f"{TRIALS_PER_EXPERIMENT} "
            f"correct"
        )


    # -----------------------------------------------------
    # SAVE RAW CSV
    # -----------------------------------------------------

    fieldnames = list(
        rows[0].keys()
    )

    with open(
        RAW_OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)


    # -----------------------------------------------------
    # FINAL SUMMARY
    # -----------------------------------------------------

    total = len(rows)

    passed = sum(
        1
        for row in rows
        if row["detection_correct"]
    )

    failed = total - passed

    print()
    print("=" * 72)
    print("EXPERIMENT CAMPAIGN COMPLETE")
    print("=" * 72)

    print(
        "TOTAL TRIALS :",
        total
    )

    print(
        "PASS         :",
        passed
    )

    print(
        "FAIL         :",
        failed
    )

    print(
        "RAW CSV      :",
        RAW_OUTPUT_FILE
    )

    print()
    print(
        "NOTE: Results are from controlled "
        "software-injected diagnostic tests."
    )

    print(
        "They are not physical sensor measurements."
    )

    print("=" * 72)


if __name__ == "__main__":
    main()