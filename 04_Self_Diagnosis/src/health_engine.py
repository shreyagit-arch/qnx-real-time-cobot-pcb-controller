"""
EdgeGuard Self-Diagnosis Health Engine
Phase 2 extension to the frozen QNX PCB/Cobot controller.

This module evaluates five health domains:
1. Thermal
2. Sensor
3. Power
4. Communication
5. Timing

The current values are representative inputs for development/testing.
Physical sensor integration is handled separately.
"""

from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class Severity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"


class Action(Enum):
    LOG = "LOG"
    ALERT = "ALERT"
    DEGRADE = "DEGRADE"
    SAFE_MODE = "SAFE_MODE"


@dataclass
class DiagnosticResult:
    domain: str
    measured_value: float
    unit: str
    status: str
    severity: Severity
    action: Action
    diagnostic_score: float
    message: str


class HealthEngine:

    # Prototype diagnostic thresholds.
    # These are engineering test thresholds, not universal safety limits.

    THERMAL_WARNING_C = 60.0
    THERMAL_CRITICAL_C = 75.0

    SENSOR_NOISE_WARNING = 8.0
    SENSOR_NOISE_CRITICAL = 15.0

    POWER_DEVIATION_WARNING_PERCENT = 10.0
    POWER_DEVIATION_CRITICAL_PERCENT = 20.0

    COMM_WARNING_ERRORS = 1
    COMM_CRITICAL_ERRORS = 3

    CONTROL_DEADLINE_US = 80_000

    def _score(self, value, warning, critical):
        """Return a normalized diagnostic score from 0 to 100."""

        if value <= warning:
            if warning == 0:
                return 0.0
            return min((value / warning) * 50.0, 50.0)

        if critical == warning:
            return 100.0

        if value < critical:
            return 50.0 + (
                ((value - warning) / (critical - warning)) * 50.0
            )

        return 100.0

    def check_thermal(self, temperature_c):
        score = self._score(
            temperature_c,
            self.THERMAL_WARNING_C,
            self.THERMAL_CRITICAL_C
        )

        if temperature_c >= self.THERMAL_CRITICAL_C:
            return DiagnosticResult(
                "THERMAL",
                temperature_c,
                "C",
                "FAULT",
                Severity.CRITICAL,
                Action.SAFE_MODE,
                score,
                "Critical thermal anomaly detected"
            )

        if temperature_c >= self.THERMAL_WARNING_C:
            return DiagnosticResult(
                "THERMAL",
                temperature_c,
                "C",
                "WARNING",
                Severity.WARNING,
                Action.ALERT,
                score,
                "Temperature approaching critical region"
            )

        return DiagnosticResult(
            "THERMAL",
            temperature_c,
            "C",
            "HEALTHY",
            Severity.INFO,
            Action.LOG,
            score,
            "Thermal condition normal"
        )

    def check_sensor(self, noise_magnitude):
        score = self._score(
            noise_magnitude,
            self.SENSOR_NOISE_WARNING,
            self.SENSOR_NOISE_CRITICAL
        )

        if noise_magnitude >= self.SENSOR_NOISE_CRITICAL:
            return DiagnosticResult(
                "SENSOR",
                noise_magnitude,
                "noise-index",
                "FAULT",
                Severity.DEGRADED,
                Action.DEGRADE,
                score,
                "Sensor signal considered unreliable"
            )

        if noise_magnitude >= self.SENSOR_NOISE_WARNING:
            return DiagnosticResult(
                "SENSOR",
                noise_magnitude,
                "noise-index",
                "WARNING",
                Severity.WARNING,
                Action.ALERT,
                score,
                "Elevated sensor noise detected"
            )

        return DiagnosticResult(
            "SENSOR",
            noise_magnitude,
            "noise-index",
            "HEALTHY",
            Severity.INFO,
            Action.LOG,
            score,
            "Sensor signal normal"
        )

    def check_power(self, deviation_percent):
        deviation_percent = abs(deviation_percent)

        score = self._score(
            deviation_percent,
            self.POWER_DEVIATION_WARNING_PERCENT,
            self.POWER_DEVIATION_CRITICAL_PERCENT
        )

        if deviation_percent >= self.POWER_DEVIATION_CRITICAL_PERCENT:
            return DiagnosticResult(
                "POWER",
                deviation_percent,
                "%",
                "FAULT",
                Severity.CRITICAL,
                Action.SAFE_MODE,
                score,
                "Critical power/current deviation detected"
            )

        if deviation_percent >= self.POWER_DEVIATION_WARNING_PERCENT:
            return DiagnosticResult(
                "POWER",
                deviation_percent,
                "%",
                "WARNING",
                Severity.WARNING,
                Action.ALERT,
                score,
                "Abnormal power/current deviation detected"
            )

        return DiagnosticResult(
            "POWER",
            deviation_percent,
            "%",
            "HEALTHY",
            Severity.INFO,
            Action.LOG,
            score,
            "Power condition normal"
        )

    def check_communication(self, error_count):
        score = self._score(
            error_count,
            self.COMM_WARNING_ERRORS,
            self.COMM_CRITICAL_ERRORS
        )

        if error_count >= self.COMM_CRITICAL_ERRORS:
            return DiagnosticResult(
                "COMMUNICATION",
                error_count,
                "errors",
                "FAULT",
                Severity.CRITICAL,
                Action.SAFE_MODE,
                score,
                "Repeated communication failure detected"
            )

        if error_count >= self.COMM_WARNING_ERRORS:
            return DiagnosticResult(
                "COMMUNICATION",
                error_count,
                "errors",
                "WARNING",
                Severity.WARNING,
                Action.ALERT,
                score,
                "Communication error detected"
            )

        return DiagnosticResult(
            "COMMUNICATION",
            error_count,
            "errors",
            "HEALTHY",
            Severity.INFO,
            Action.LOG,
            score,
            "Communication channel normal"
        )

    def check_timing(self, control_execution_us):
        score = self._score(
            control_execution_us,
            self.CONTROL_DEADLINE_US * 0.80,
            self.CONTROL_DEADLINE_US
        )

        if control_execution_us > self.CONTROL_DEADLINE_US:
            return DiagnosticResult(
                "TIMING",
                control_execution_us,
                "us",
                "FAULT",
                Severity.CRITICAL,
                Action.SAFE_MODE,
                100.0,
                "Control deadline violation detected"
            )

        if control_execution_us >= self.CONTROL_DEADLINE_US * 0.80:
            return DiagnosticResult(
                "TIMING",
                control_execution_us,
                "us",
                "WARNING",
                Severity.WARNING,
                Action.ALERT,
                score,
                "Control execution approaching deadline"
            )

        return DiagnosticResult(
            "TIMING",
            control_execution_us,
            "us",
            "HEALTHY",
            Severity.INFO,
            Action.LOG,
            score,
            "Control timing normal"
        )

    def evaluate_system(
        self,
        temperature_c,
        sensor_noise,
        power_deviation_percent,
        communication_errors,
        control_execution_us
    ):
        return [
            self.check_thermal(temperature_c),
            self.check_sensor(sensor_noise),
            self.check_power(power_deviation_percent),
            self.check_communication(communication_errors),
            self.check_timing(control_execution_us)
        ]


def print_report(results):
    print()
    print("=" * 78)
    print("EDGEGUARD SELF-DIAGNOSIS REPORT")
    print("Timestamp:", datetime.now().isoformat(timespec="seconds"))
    print("=" * 78)

    for result in results:
        print(
            f"{result.domain:<15}"
            f"STATUS={result.status:<8} "
            f"SEVERITY={result.severity.value:<9} "
            f"ACTION={result.action.value:<10} "
            f"SCORE={result.diagnostic_score:6.2f}"
        )

        print(
            f"{'':15}"
            f"VALUE={result.measured_value} {result.unit} | "
            f"{result.message}"
        )

    print("=" * 78)


if __name__ == "__main__":

    engine = HealthEngine()

    # Representative NORMAL test case.
    # These values are not claimed as physical measurements.

    results = engine.evaluate_system(
        temperature_c=42.0,
        sensor_noise=3.0,
        power_deviation_percent=4.0,
        communication_errors=0,
        control_execution_us=45_000
    )

    print_report(results)