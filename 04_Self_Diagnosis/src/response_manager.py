"""
EdgeGuard Response Manager
Phase 2 self-diagnosis extension.

Takes diagnostic results from health_engine.py and determines
the overall system operating state.

This module is currently evaluated using representative
software-injected diagnostic inputs.
"""

from enum import Enum

from health_engine import (
    HealthEngine,
    Action,
    Severity,
    print_report
)


class SystemState(Enum):
    NORMAL = "NORMAL"
    ALERT = "ALERT"
    DEGRADED = "DEGRADED"
    SAFE_MODE = "SAFE_MODE"


class ResponseManager:

    def __init__(self):
        self.state = SystemState.NORMAL
        self.safe_mode_latched = False
        self.trigger_domain = "NONE"

    def evaluate(self, diagnostic_results):

        # Highest priority:
        # Any SAFE_MODE request causes a latched safe state.
        for result in diagnostic_results:
            if result.action == Action.SAFE_MODE:
                self.state = SystemState.SAFE_MODE
                self.safe_mode_latched = True
                self.trigger_domain = result.domain
                return self.state

        # If already latched, normal readings cannot automatically
        # return the system to operation.
        if self.safe_mode_latched:
            self.state = SystemState.SAFE_MODE
            return self.state

        # Second priority:
        # A degraded subsystem causes degraded operation.
        for result in diagnostic_results:
            if (
                result.action == Action.DEGRADE
                or result.severity == Severity.DEGRADED
            ):
                self.state = SystemState.DEGRADED
                self.trigger_domain = result.domain
                return self.state

        # Third priority:
        # Warning conditions produce an alert.
        for result in diagnostic_results:
            if result.action == Action.ALERT:
                self.state = SystemState.ALERT
                self.trigger_domain = result.domain
                return self.state

        self.state = SystemState.NORMAL
        self.trigger_domain = "NONE"
        return self.state

    def command_allowed(self, command):
        """
        Representative command-blocking policy.

        In SAFE_MODE, movement commands are blocked.
        STOP and RESET remain permitted.
        """

        command = command.upper()

        if not self.safe_mode_latched:
            return True

        allowed_commands = {"STOP", "RESET"}

        return command in allowed_commands

    def reset(self, diagnostic_results):
        """
        Clear SAFE_MODE only when all diagnostic domains
        are no longer reporting FAULT.
        """

        active_faults = [
            result
            for result in diagnostic_results
            if result.status == "FAULT"
        ]

        if active_faults:
            return False

        self.safe_mode_latched = False
        self.state = SystemState.NORMAL
        self.trigger_domain = "NONE"

        return True


def print_system_response(manager):

    print()
    print("=" * 78)
    print("EDGEGUARD RESPONSE MANAGER")
    print("=" * 78)

    print(f"SYSTEM STATE       : {manager.state.value}")
    print(f"SAFE MODE LATCHED  : {manager.safe_mode_latched}")
    print(f"TRIGGER DOMAIN     : {manager.trigger_domain}")

    print("-" * 78)

    for command in ["PICK", "MOVE", "PLACE", "STOP", "RESET"]:
        status = (
            "ALLOWED"
            if manager.command_allowed(command)
            else "BLOCKED"
        )

        print(f"{command:<10}: {status}")

    print("=" * 78)


if __name__ == "__main__":

    engine = HealthEngine()
    manager = ResponseManager()

    # Representative communication-fault test.
    # These are software-injected values, not physical measurements.

    results = engine.evaluate_system(
        temperature_c=42.0,
        sensor_noise=3.0,
        power_deviation_percent=4.0,
        communication_errors=5,
        control_execution_us=45_000
    )

    print_report(results)

    manager.evaluate(results)

    print_system_response(manager)