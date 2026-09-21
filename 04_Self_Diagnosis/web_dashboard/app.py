"""
EdgeGuard Web Digital Twin - Flask Backend

Connects the browser dashboard to:
    health_engine.py
    response_manager.py
    diagnostic_experiments_summary.csv

IMPORTANT EVIDENCE BOUNDARY
---------------------------
Fault inputs are controlled software injections.
Diagnostic latency is Python execution time on the development PC.
It is NOT QNX latency, Arduino latency, physical sensor response time,
or certified safety-response latency.
"""

from flask import Flask, render_template, jsonify, request
import csv
import os
import sys
import time


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SELF_DIAGNOSIS_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..")
)

SRC_DIR = os.path.join(
    SELF_DIAGNOSIS_DIR,
    "src"
)

RESULTS_DIR = os.path.join(
    SELF_DIAGNOSIS_DIR,
    "results"
)

SUMMARY_CSV = os.path.join(
    RESULTS_DIR,
    "diagnostic_experiments_summary.csv"
)

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


# =========================================================
# EDGEGUARD BACKEND
# =========================================================

from health_engine import HealthEngine
from response_manager import ResponseManager


# =========================================================
# FLASK
# =========================================================

app = Flask(__name__)

engine = HealthEngine()
manager = ResponseManager()


# =========================================================
# REPRESENTATIVE SOFTWARE TEST INPUTS
# =========================================================

DEFAULT_VALUES = {
    "temperature_c": 42.0,
    "sensor_noise": 3.0,
    "power_deviation_percent": 4.0,
    "communication_errors": 0,
    "control_execution_us": 45000,
}

current_values = DEFAULT_VALUES.copy()

robot_state = "READY"

event_log = []


# =========================================================
# EVENT LOG
# =========================================================

def add_event(message, level="INFO"):

    event = {
        "timestamp": time.strftime("%H:%M:%S"),
        "level": level,
        "message": message,
    }

    event_log.insert(0, event)

    # Prevent unlimited memory growth
    if len(event_log) > 100:
        del event_log[100:]


# =========================================================
# SERIALIZATION
# =========================================================

def serialize_result(result):

    return {
        "domain": result.domain,
        "measured_value": result.measured_value,
        "unit": result.unit,
        "status": result.status,
        "severity": result.severity.value,
        "action": result.action.value,
        "diagnostic_score": result.diagnostic_score,
        "message": result.message,
    }


# =========================================================
# DIAGNOSTIC EVALUATION
# =========================================================

def evaluate():

    start_ns = time.perf_counter_ns()

    results = engine.evaluate_system(
        temperature_c=current_values["temperature_c"],
        sensor_noise=current_values["sensor_noise"],
        power_deviation_percent=
            current_values["power_deviation_percent"],
        communication_errors=
            current_values["communication_errors"],
        control_execution_us=
            current_values["control_execution_us"],
    )

    manager.evaluate(results)

    end_ns = time.perf_counter_ns()

    latency_us = (end_ns - start_ns) / 1000.0

    return results, latency_us


# =========================================================
# DOMINANT DIAGNOSTIC RESULT
# =========================================================

def dominant_result(results):

    severity_rank = {
        "INFO": 0,
        "WARNING": 1,
        "DEGRADED": 2,
        "CRITICAL": 3,
    }

    return max(
        results,
        key=lambda result:
            severity_rank.get(
                result.severity.value,
                0
            )
    )


# =========================================================
# CURRENT SYSTEM STATE
# =========================================================

def build_state():

    results, latency_us = evaluate()

    dominant = dominant_result(results)

    if dominant.status == "HEALTHY":
        fault_domain = "NONE"
    else:
        fault_domain = dominant.domain

    command_enabled = not manager.safe_mode_latched

    return {
        "system_state": manager.state.value,
        "fault_domain": fault_domain,
        "severity": dominant.severity.value,
        "action": dominant.action.value,

        "safe_mode_latched":
            manager.safe_mode_latched,

        "safety_latch":
            "LATCHED"
            if manager.safe_mode_latched
            else "CLEAR",

        "robot_state": robot_state,

        "command_status":
            "BLOCKED"
            if manager.safe_mode_latched
            else "ENABLED",

        "command_enabled": command_enabled,

        "diagnostic_latency_us":
            round(latency_us, 3),

        "diagnostic_latency_label":
            "PC Python diagnostic-engine execution time",

        "values": current_values.copy(),

        "health": [
            serialize_result(result)
            for result in results
        ],

        "events": event_log[:30],

        "evidence_boundary": (
            "Controlled software injection. "
            "Not physical sensor measurement, "
            "QNX response latency, Arduino response latency, "
            "or certified safety-response measurement."
        ),
    }


# =========================================================
# EXPERIMENTAL EVIDENCE
# =========================================================

def load_experiment_summary():

    if not os.path.exists(SUMMARY_CSV):

        return {
            "available": False,
            "experiments": [],
            "total_trials": 0,
            "correct_responses": 0,
            "overall_rate_percent": 0.0,
        }

    experiments = []

    with open(
        SUMMARY_CSV,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            experiments.append({
                "experiment_id":
                    row["experiment_id"],

                "domain":
                    row["injected_fault_domain"],

                "trials":
                    int(row["trials"]),

                "correct_detections":
                    int(row["correct_detections"]),

                "failed_detections":
                    int(row["failed_detections"]),

                "detection_rate_percent":
                    float(row["detection_rate_percent"]),

                "mean_latency_us":
                    float(
                        row[
                            "mean_diagnostic_latency_us"
                        ]
                    ),

                "min_latency_us":
                    float(
                        row[
                            "minimum_diagnostic_latency_us"
                        ]
                    ),

                "max_latency_us":
                    float(
                        row[
                            "maximum_diagnostic_latency_us"
                        ]
                    ),

                "jitter_us":
                    float(
                        row[
                            "latency_range_jitter_us"
                        ]
                    ),

                "std_dev_us":
                    float(
                        row[
                            "latency_std_dev_us"
                        ]
                    ),

                "expected_state":
                    row["expected_system_state"],

                "observed_state":
                    row["observed_system_state"],
            })


    total_trials = sum(
        item["trials"]
        for item in experiments
    )

    correct_responses = sum(
        item["correct_detections"]
        for item in experiments
    )

    if total_trials:

        overall_rate = (
            correct_responses
            / total_trials
            * 100.0
        )

    else:

        overall_rate = 0.0


    return {
        "available": True,
        "experiments": experiments,
        "total_trials": total_trials,
        "correct_responses": correct_responses,
        "overall_rate_percent":
            round(overall_rate, 2),

        "interpretation": (
            "Observed expected-response rate from controlled "
            "software-injected diagnostic trials."
        ),

        "latency_interpretation": (
            "Latency statistics represent Python diagnostic "
            "engine execution on the development PC."
        ),
    }


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# =========================================================
# API - CURRENT STATE
# =========================================================

@app.route("/api/state")
def api_state():

    return jsonify(
        build_state()
    )


# =========================================================
# API - EVIDENCE
# =========================================================

@app.route("/api/evidence")
def api_evidence():

    return jsonify(
        load_experiment_summary()
    )


# =========================================================
# API - NORMAL RUN
# =========================================================

@app.route(
    "/api/normal-run",
    methods=["POST"]
)
def normal_run():

    global current_values
    global robot_state

    if manager.safe_mode_latched:

        robot_state = "STOPPED"

        add_event(
            "NORMAL RUN BLOCKED - "
            "SAFE_MODE safety latch is active.",
            "CRITICAL"
        )

        state = build_state()
        state["accepted"] = False

        return jsonify(state)


    current_values = DEFAULT_VALUES.copy()

    robot_state = "READY"

    add_event(
        "Normal PCB pick-and-place cycle requested.",
        "INFO"
    )

    state = build_state()
    state["accepted"] = True

    return jsonify(state)


# =========================================================
# API - ROBOT STATE
# Used by browser animation to represent the digital twin.
# =========================================================

@app.route(
    "/api/robot-state",
    methods=["POST"]
)
def set_robot_state():

    global robot_state

    data = request.get_json(
        silent=True
    ) or {}

    requested_state = data.get(
        "state",
        "READY"
    )

    allowed_states = {
        "READY",
        "COMPONENT_HELD",
        "MOVING",
        "AT_DESTINATION",
        "STOPPED",
        "DEGRADED",
    }

    if requested_state not in allowed_states:

        return jsonify({
            "success": False,
            "error": "Invalid robot state"
        }), 400


    if (
        manager.safe_mode_latched
        and requested_state
        not in {"STOPPED"}
    ):

        robot_state = "STOPPED"

        add_event(
            f"Robot command {requested_state} BLOCKED "
            "by safety latch.",
            "CRITICAL"
        )

        return jsonify({
            "success": False,
            "blocked": True,
            "state": build_state()
        })


    robot_state = requested_state

    return jsonify({
        "success": True,
        "state": build_state()
    })


# =========================================================
# API - FAULT INJECTION
# =========================================================

@app.route(
    "/api/inject/<fault_type>",
    methods=["POST"]
)
def inject_fault(fault_type):

    global current_values
    global robot_state

    current_values = DEFAULT_VALUES.copy()

    fault_type = fault_type.lower()


    # -----------------------------------------------------
    # THERMAL
    # -----------------------------------------------------

    if fault_type == "thermal":

        current_values[
            "temperature_c"
        ] = 82.0

        robot_state = "STOPPED"

        add_event(
            "THERMAL injection: 82 C",
            "FAULT"
        )


    # -----------------------------------------------------
    # SENSOR
    # -----------------------------------------------------

    elif fault_type == "sensor":

        current_values[
            "sensor_noise"
        ] = 18.0

        robot_state = "DEGRADED"

        add_event(
            "SENSOR-NOISE injection: score 18",
            "WARNING"
        )


    # -----------------------------------------------------
    # POWER
    # -----------------------------------------------------

    elif fault_type == "power":

        current_values[
            "power_deviation_percent"
        ] = 27.0

        robot_state = "STOPPED"

        add_event(
            "POWER injection: 27 percent deviation",
            "FAULT"
        )


    # -----------------------------------------------------
    # COMMUNICATION
    # -----------------------------------------------------

    elif fault_type == "communication":

        current_values[
            "communication_errors"
        ] = 5

        robot_state = "STOPPED"

        add_event(
            "COMMUNICATION injection: 5 errors",
            "FAULT"
        )


    # -----------------------------------------------------
    # TIMING
    # -----------------------------------------------------

    elif fault_type == "timing":

        current_values[
            "control_execution_us"
        ] = 100000

        robot_state = "STOPPED"

        add_event(
            "TIMING injection: Control = 100000 us; "
            "prototype requirement = 80000 us.",
            "FAULT"
        )


    else:

        return jsonify({
            "success": False,
            "error": "Unknown fault type"
        }), 400


    state = build_state()

    if state["system_state"] == "SAFE_MODE":

        add_event(
            f"{state['fault_domain']} -> "
            "CRITICAL -> SAFE_MODE -> "
            "SAFETY LATCHED -> MOVEMENT BLOCKED",
            "CRITICAL"
        )

    elif state["system_state"] == "DEGRADED":

        add_event(
            f"{state['fault_domain']} -> "
            "DEGRADED OPERATION",
            "WARNING"
        )


    state = build_state()
    state["success"] = True

    return jsonify(state)


# =========================================================
# API - RESET
# =========================================================

@app.route(
    "/api/reset",
    methods=["POST"]
)
def reset():

    global current_values
    global robot_state

    current_values = DEFAULT_VALUES.copy()

    healthy_results = engine.evaluate_system(
        temperature_c=
            current_values["temperature_c"],

        sensor_noise=
            current_values["sensor_noise"],

        power_deviation_percent=
            current_values[
                "power_deviation_percent"
            ],

        communication_errors=
            current_values[
                "communication_errors"
            ],

        control_execution_us=
            current_values[
                "control_execution_us"
            ],
    )


    success = manager.reset(
        healthy_results
    )


    if success:

        robot_state = "READY"

        add_event(
            "Explicit RESET accepted. "
            "Safety latch cleared. "
            "Robot returned to READY.",
            "INFO"
        )

    else:

        robot_state = "STOPPED"

        add_event(
            "RESET rejected because "
            "an active fault remains.",
            "CRITICAL"
        )


    state = build_state()
    state["reset_success"] = success

    return jsonify(state)


# =========================================================
# API - CLEAR EVENT LOG
# =========================================================

@app.route(
    "/api/clear-log",
    methods=["POST"]
)
def clear_log():

    event_log.clear()

    add_event(
        "Diagnostic event log cleared.",
        "INFO"
    )

    return jsonify(
        build_state()
    )


# =========================================================
# INITIAL EVENT
# =========================================================

add_event(
    "EdgeGuard diagnostic supervisor initialized.",
    "INFO"
)

add_event(
    "Five health domains active: "
    "THERMAL | SENSOR | POWER | "
    "COMMUNICATION | TIMING",
    "INFO"
)

add_event(
    "Robot state READY. "
    "Safety latch CLEAR.",
    "INFO"
)


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 72)
    print("EDGEGUARD WEB DIGITAL TWIN")
    print("=" * 72)
    print("Dashboard : http://127.0.0.1:5000")
    print("Mode      : Local presentation server")
    print("Backend   : EdgeGuard HealthEngine + ResponseManager")
    print("=" * 72)
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )