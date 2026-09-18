"""
EdgeGuard Safety-Latch Verification Test

Demonstrates:
NORMAL
-> communication fault
-> SAFE_MODE latch
-> physical/software condition returns healthy
-> latch remains active
-> explicit reset
-> NORMAL

Inputs are representative software-injected test values.
"""

from health_engine import HealthEngine
from response_manager import ResponseManager


def show_step(title, manager):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)

    print("SYSTEM STATE      :", manager.state.value)
    print("SAFE MODE LATCHED :", manager.safe_mode_latched)
    print("TRIGGER DOMAIN    :", manager.trigger_domain)

    for command in ["PICK", "MOVE", "PLACE", "STOP", "RESET"]:
        status = (
            "ALLOWED"
            if manager.command_allowed(command)
            else "BLOCKED"
        )

        print(f"{command:<10}: {status}")


engine = HealthEngine()
manager = ResponseManager()


# ---------------------------------------------------------
# STEP 1 - NORMAL OPERATION
# ---------------------------------------------------------

normal_results = engine.evaluate_system(
    temperature_c=42.0,
    sensor_noise=3.0,
    power_deviation_percent=4.0,
    communication_errors=0,
    control_execution_us=45_000
)

manager.evaluate(normal_results)

show_step(
    "STEP 1 - NORMAL OPERATION",
    manager
)


# ---------------------------------------------------------
# STEP 2 - COMMUNICATION FAULT INJECTED
# ---------------------------------------------------------

fault_results = engine.evaluate_system(
    temperature_c=42.0,
    sensor_noise=3.0,
    power_deviation_percent=4.0,
    communication_errors=5,
    control_execution_us=45_000
)

manager.evaluate(fault_results)

show_step(
    "STEP 2 - COMMUNICATION FAULT -> SAFE MODE",
    manager
)


# ---------------------------------------------------------
# STEP 3 - FAULT CONDITION DISAPPEARS
# ---------------------------------------------------------

recovered_results = engine.evaluate_system(
    temperature_c=42.0,
    sensor_noise=3.0,
    power_deviation_percent=4.0,
    communication_errors=0,
    control_execution_us=45_000
)

manager.evaluate(recovered_results)

show_step(
    "STEP 3 - CONDITION HEALTHY BUT LATCH REMAINS",
    manager
)


# ---------------------------------------------------------
# STEP 4 - EXPLICIT RESET
# ---------------------------------------------------------

reset_success = manager.reset(recovered_results)

print()
print("RESET REQUEST RESULT :", reset_success)

show_step(
    "STEP 4 - RESET COMPLETED",
    manager
)


# ---------------------------------------------------------
# FINAL VERIFICATION
# ---------------------------------------------------------

assert reset_success is True
assert manager.safe_mode_latched is False
assert manager.state.value == "NORMAL"
assert manager.command_allowed("PICK") is True
assert manager.command_allowed("MOVE") is True
assert manager.command_allowed("PLACE") is True

print()
print("=" * 70)
print("SAFETY-LATCH VERIFICATION: PASS")
print("=" * 70)