"""
EdgeGuard Diagnostic Experiment Analyzer

Reads:
    diagnostic_experiments_raw.csv

Creates:
    diagnostic_experiments_summary.csv

IMPORTANT:
Latency values represent execution time of the Python
diagnostic/response logic on the development PC.

They are NOT:
- QNX task latency
- Arduino latency
- physical sensor response time
- certified safety response time
"""

import csv
import os
import statistics
from collections import defaultdict


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

SCRIPT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

RESULTS_DIR = os.path.abspath(
    os.path.join(
        SCRIPT_DIR,
        "..",
        "results"
    )
)

RAW_FILE = os.path.join(
    RESULTS_DIR,
    "diagnostic_experiments_raw.csv"
)

SUMMARY_FILE = os.path.join(
    RESULTS_DIR,
    "diagnostic_experiments_summary.csv"
)


# ---------------------------------------------------------
# LOAD RAW DATA
# ---------------------------------------------------------

def load_data():

    if not os.path.exists(RAW_FILE):
        raise FileNotFoundError(
            f"Raw experiment file not found: {RAW_FILE}"
        )

    with open(
        RAW_FILE,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        rows = list(reader)

    if not rows:
        raise ValueError(
            "Raw experiment CSV contains no data."
        )

    return rows


# ---------------------------------------------------------
# GROUP BY EXPERIMENT
# ---------------------------------------------------------

def group_experiments(rows):

    groups = defaultdict(list)

    for row in rows:
        groups[row["experiment_id"]].append(row)

    return groups


# ---------------------------------------------------------
# BOOLEAN CONVERSION
# ---------------------------------------------------------

def to_bool(value):

    return str(value).strip().lower() == "true"


# ---------------------------------------------------------
# ANALYZE ONE EXPERIMENT
# ---------------------------------------------------------

def analyze_experiment(
    experiment_id,
    rows
):

    latencies = [
        float(row["diagnostic_latency_us"])
        for row in rows
    ]

    total_trials = len(rows)

    correct_detections = sum(
        1
        for row in rows
        if to_bool(
            row["detection_correct"]
        )
    )

    failed_detections = (
        total_trials
        - correct_detections
    )

    detection_rate = (
        correct_detections
        / total_trials
        * 100.0
    )

    mean_latency = statistics.mean(
        latencies
    )

    minimum_latency = min(
        latencies
    )

    maximum_latency = max(
        latencies
    )

    jitter = (
        maximum_latency
        - minimum_latency
    )

    if len(latencies) > 1:

        std_dev = statistics.stdev(
            latencies
        )

    else:

        std_dev = 0.0


    first = rows[0]


    return {
        "experiment_id":
            experiment_id,

        "injected_fault_domain":
            first[
                "injected_fault_domain"
            ],

        "trials":
            total_trials,

        "correct_detections":
            correct_detections,

        "failed_detections":
            failed_detections,

        "detection_rate_percent":
            round(
                detection_rate,
                2
            ),

        "mean_diagnostic_latency_us":
            round(
                mean_latency,
                3
            ),

        "minimum_diagnostic_latency_us":
            round(
                minimum_latency,
                3
            ),

        "maximum_diagnostic_latency_us":
            round(
                maximum_latency,
                3
            ),

        "latency_range_jitter_us":
            round(
                jitter,
                3
            ),

        "latency_std_dev_us":
            round(
                std_dev,
                3
            ),

        "expected_system_state":
            first[
                "expected_system_state"
            ],

        "observed_system_state":
            first[
                "observed_system_state"
            ],
    }


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    rows = load_data()

    groups = group_experiments(
        rows
    )

    summaries = []


    print()
    print("=" * 78)
    print(
        "EDGEGUARD DIAGNOSTIC EXPERIMENT ANALYSIS"
    )
    print("=" * 78)


    for experiment_id in sorted(
        groups.keys()
    ):

        summary = analyze_experiment(
            experiment_id,
            groups[experiment_id]
        )

        summaries.append(
            summary
        )


        print()
        print(
            "EXPERIMENT :",
            summary[
                "experiment_id"
            ]
        )

        print(
            "DOMAIN     :",
            summary[
                "injected_fault_domain"
            ]
        )

        print(
            "TRIALS     :",
            summary["trials"]
        )

        print(
            "DETECTED   :",
            f"{summary['correct_detections']}"
            f"/{summary['trials']}"
        )

        print(
            "RATE       :",
            f"{summary['detection_rate_percent']}%"
        )

        print(
            "MEAN LAT   :",
            f"{summary['mean_diagnostic_latency_us']} us"
        )

        print(
            "MIN LAT    :",
            f"{summary['minimum_diagnostic_latency_us']} us"
        )

        print(
            "MAX LAT    :",
            f"{summary['maximum_diagnostic_latency_us']} us"
        )

        print(
            "JITTER     :",
            f"{summary['latency_range_jitter_us']} us"
        )

        print(
            "STD DEV    :",
            f"{summary['latency_std_dev_us']} us"
        )

        print(
            "STATE      :",
            summary[
                "observed_system_state"
            ]
        )


    # -----------------------------------------------------
    # SAVE SUMMARY
    # -----------------------------------------------------

    fieldnames = list(
        summaries[0].keys()
    )

    with open(
        SUMMARY_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(
            summaries
        )


    # -----------------------------------------------------
    # CAMPAIGN SUMMARY
    # -----------------------------------------------------

    total_trials = sum(
        item["trials"]
        for item in summaries
    )

    total_correct = sum(
        item["correct_detections"]
        for item in summaries
    )

    overall_detection_rate = (
        total_correct
        / total_trials
        * 100.0
    )


    print()
    print("=" * 78)
    print("CAMPAIGN SUMMARY")
    print("=" * 78)

    print(
        "EXPERIMENTS       :",
        len(summaries)
    )

    print(
        "TOTAL TRIALS      :",
        total_trials
    )

    print(
        "CORRECT RESPONSES :",
        total_correct
    )

    print(
        "OVERALL RATE      :",
        f"{overall_detection_rate:.2f}%"
    )

    print(
        "SUMMARY CSV       :",
        SUMMARY_FILE
    )

    print()
    print(
        "Interpretation: latency is Python "
        "diagnostic-engine execution latency "
        "on this development PC."
    )

    print(
        "It must not be presented as physical "
        "fault-response or QNX real-time latency."
    )

    print("=" * 78)


if __name__ == "__main__":
    main()