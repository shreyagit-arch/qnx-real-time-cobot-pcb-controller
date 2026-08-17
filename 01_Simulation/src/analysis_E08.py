import csv
import os
import statistics


BASE_DIR = os.path.dirname(__file__)

CSV_FILE = os.path.join(
    BASE_DIR,
    "..",
    "results",
    "raw",
    "E06_REPEATED_NOMINAL.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "..",
    "results",
    "analysis"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "E06_STATISTICAL_SUMMARY.csv"
)


def calculate_statistics(values):

    return {
        "mean": statistics.mean(values),
        "minimum": min(values),
        "maximum": max(values),
        "range_jitter": max(values) - min(values),
        "std_dev": statistics.stdev(values)
        if len(values) > 1 else 0
    }


def main():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(CSV_FILE, "r", newline="") as file:

        rows = list(csv.DictReader(file))

    print()
    print("================================")
    print(" QNX PCB COBOT STATISTICAL ANALYSIS")
    print("================================")
    print()

    print(f"INPUT FILE : {CSV_FILE}")
    print(f"TRIALS     : {len(rows)}")
    print()

    measurements = {
        "VISION": [
            float(row["vision_us"])
            for row in rows
        ],

        "IPC": [
            float(row["ipc_us"])
            for row in rows
        ],

        "CONTROL": [
            float(row["control_us"])
            for row in rows
        ],

        "END_TO_END": [
            float(row["end_to_end_us"])
            for row in rows
        ]
    }

    summary_rows = []

    for name, values in measurements.items():

        stats = calculate_statistics(values)

        if name == "VISION":
            deadline = 50000

        elif name == "IPC":
            deadline = 5000

        elif name == "CONTROL":
            deadline = 80000

        else:
            deadline = 150000

        misses = sum(
            value > deadline
            for value in values
        )

        miss_percentage = (
            misses / len(values)
        ) * 100

        print(f"{name}")
        print(
            f"  Mean       : {stats['mean']:.2f} us"
        )
        print(
            f"  Minimum    : {stats['minimum']:.0f} us"
        )
        print(
            f"  Maximum    : {stats['maximum']:.0f} us"
        )
        print(
            f"  Jitter     : {stats['range_jitter']:.0f} us"
        )
        print(
            f"  Std Dev    : {stats['std_dev']:.2f} us"
        )
        print(
            f"  Deadline   : {deadline} us"
        )
        print(
            f"  Misses     : {misses}/{len(values)}"
        )
        print(
            f"  Miss Rate  : {miss_percentage:.2f}%"
        )
        print()

        summary_rows.append({
            "metric": name,
            "samples": len(values),
            "mean_us": round(stats["mean"], 2),
            "minimum_us": round(stats["minimum"], 2),
            "maximum_us": round(stats["maximum"], 2),
            "jitter_us": round(
                stats["range_jitter"], 2
            ),
            "std_dev_us": round(
                stats["std_dev"], 2
            ),
            "deadline_us": deadline,
            "deadline_misses": misses,
            "deadline_miss_rate_percent":
                round(miss_percentage, 2)
        })

    fieldnames = [
        "metric",
        "samples",
        "mean_us",
        "minimum_us",
        "maximum_us",
        "jitter_us",
        "std_dev_us",
        "deadline_us",
        "deadline_misses",
        "deadline_miss_rate_percent"
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(summary_rows)

    print("================================")
    print("STATISTICAL ANALYSIS COMPLETE")
    print("================================")
    print()
    print(
        f"RESULT SAVED : {OUTPUT_FILE}"
    )
    print()


if __name__ == "__main__":
    main()