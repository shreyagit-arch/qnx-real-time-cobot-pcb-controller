"""
EdgeGuard Live Digital Twin
QNX-Based Real-Time Cobot Controller
with Self-Diagnosing Edge Supervision

Software demonstration only.

The GUI visualizes:
Camera -> Vision -> IPC -> QNX Control -> Robot
and
Thermal / Sensor / Power / Communication / Timing
-> EdgeGuard Health Engine
-> Fault Manager
-> Safety Manager

Fault buttons inject representative software test values.
They are NOT physical sensor measurements.
"""

import tkinter as tk
from tkinter import ttk
import os
import sys
import time


# =========================================================
# IMPORT EDGEGUARD BACKEND
# =========================================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

SRC_DIR = os.path.abspath(
    os.path.join(
        CURRENT_DIR,
        "..",
        "src"
    )
)

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from health_engine import HealthEngine
from response_manager import ResponseManager


# =========================================================
# APPLICATION
# =========================================================

class EdgeGuardDigitalTwin:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "EdgeGuard | QNX Cobot Self-Diagnosis Digital Twin"
        )

        self.root.geometry("1450x850")
        self.root.minsize(1200, 720)

        self.engine = HealthEngine()
        self.manager = ResponseManager()

        self.running_sequence = False

        self.pipeline_nodes = []

        self.health_labels = {}

        self.default_values = {
            "temperature": 42.0,
            "sensor_noise": 3.0,
            "power_deviation": 4.0,
            "communication_errors": 0,
            "control_execution": 45000,
        }

        self.current_values = dict(
            self.default_values
        )

        self.configure_styles()
        self.build_interface()

        self.evaluate_current_state(
            "SYSTEM INITIALIZATION"
        )


    # =====================================================
    # STYLES
    # =====================================================

    def configure_styles(self):

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 22, "bold")
        )

        style.configure(
            "Subtitle.TLabel",
            font=("Segoe UI", 10)
        )

        style.configure(
            "Section.TLabelframe.Label",
            font=("Segoe UI", 11, "bold")
        )

        style.configure(
            "Pipeline.TLabel",
            font=("Segoe UI", 10, "bold"),
            anchor="center",
            padding=12
        )

        style.configure(
            "Health.TLabel",
            font=("Segoe UI", 10, "bold"),
            anchor="center",
            padding=8
        )

        style.configure(
            "Status.TLabel",
            font=("Segoe UI", 11, "bold")
        )

        style.configure(
            "Demo.TButton",
            font=("Segoe UI", 9, "bold"),
            padding=8
        )


    # =====================================================
    # BUILD GUI
    # =====================================================

    def build_interface(self):

        main = ttk.Frame(
            self.root,
            padding=14
        )

        main.pack(
            fill="both",
            expand=True
        )


        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        header = ttk.Frame(main)

        header.pack(
            fill="x",
            pady=(0, 10)
        )

        ttk.Label(
            header,
            text="EDGEGUARD",
            style="Title.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            header,
            text=(
                "Self-Diagnosing Edge Supervision for a "
                "QNX-Based Real-Time PCB Cobot Controller"
            ),
            style="Subtitle.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            header,
            text=(
                "LIVE SOFTWARE DIGITAL TWIN  |  "
                "CONTROLLED FAULT INJECTION DEMONSTRATOR"
            ),
            style="Subtitle.TLabel"
        ).pack(anchor="w")


        # -------------------------------------------------
        # CONTROL PIPELINE
        # -------------------------------------------------

        pipeline_frame = ttk.LabelFrame(
            main,
            text=" Real-Time Control Architecture ",
            style="Section.TLabelframe"
        )

        pipeline_frame.pack(
            fill="x",
            pady=6
        )

        pipeline_inner = ttk.Frame(
            pipeline_frame,
            padding=10
        )

        pipeline_inner.pack(
            fill="x"
        )

        nodes = [
            "PCB\nCAMERA",
            "VISION\nTASK",
            "QNX IPC",
            "CONTROL\nTASK",
            "ROBOT\nINTERFACE",
            "PICK / MOVE\n/ PLACE",
        ]

        for index, text in enumerate(nodes):

            label = tk.Label(
                pipeline_inner,
                text=text,
                font=("Segoe UI", 10, "bold"),
                relief="ridge",
                borderwidth=2,
                width=15,
                height=3,
                bg="#e8e8e8"
            )

            label.grid(
                row=0,
                column=index * 2,
                padx=3,
                pady=4,
                sticky="nsew"
            )

            self.pipeline_nodes.append(
                label
            )

            if index < len(nodes) - 1:

                ttk.Label(
                    pipeline_inner,
                    text="→",
                    font=("Segoe UI", 18, "bold")
                ).grid(
                    row=0,
                    column=index * 2 + 1
                )

        for column in range(
            len(nodes) * 2 - 1
        ):
            pipeline_inner.columnconfigure(
                column,
                weight=1
            )


        # -------------------------------------------------
        # HEALTH MONITOR
        # -------------------------------------------------

        health_frame = ttk.LabelFrame(
            main,
            text=" EdgeGuard Multi-Domain Health Monitor ",
            style="Section.TLabelframe"
        )

        health_frame.pack(
            fill="x",
            pady=6
        )

        health_inner = ttk.Frame(
            health_frame,
            padding=10
        )

        health_inner.pack(
            fill="x"
        )

        domains = [
            "THERMAL",
            "SENSOR",
            "POWER",
            "COMMUNICATION",
            "TIMING",
        ]

        for column, domain in enumerate(domains):

            label = tk.Label(
                health_inner,
                text=f"{domain}\nHEALTHY",
                font=("Segoe UI", 10, "bold"),
                relief="ridge",
                borderwidth=2,
                height=3,
                bg="#d9ead3"
            )

            label.grid(
                row=0,
                column=column,
                padx=5,
                sticky="nsew"
            )

            health_inner.columnconfigure(
                column,
                weight=1
            )

            self.health_labels[
                domain
            ] = label


        # -------------------------------------------------
        # MIDDLE AREA
        # -------------------------------------------------

        middle = ttk.Frame(main)

        middle.pack(
            fill="both",
            expand=True,
            pady=6
        )

        middle.columnconfigure(
            0,
            weight=1
        )

        middle.columnconfigure(
            1,
            weight=1
        )

        middle.rowconfigure(
            0,
            weight=1
        )


        # -------------------------------------------------
        # DIAGNOSTIC ENGINE PANEL
        # -------------------------------------------------

        diagnostic_frame = ttk.LabelFrame(
            middle,
            text=" Diagnostic Decision Layer ",
            style="Section.TLabelframe"
        )

        diagnostic_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 5)
        )

        diagnostic_inner = ttk.Frame(
            diagnostic_frame,
            padding=12
        )

        diagnostic_inner.pack(
            fill="both",
            expand=True
        )


        self.system_state_var = tk.StringVar(
            value="NORMAL"
        )

        self.fault_var = tk.StringVar(
            value="NONE"
        )

        self.severity_var = tk.StringVar(
            value="INFO"
        )

        self.action_var = tk.StringVar(
            value="LOG"
        )

        self.latch_var = tk.StringVar(
            value="CLEAR"
        )

        self.robot_var = tk.StringVar(
            value="READY"
        )

        self.latency_var = tk.StringVar(
            value="--"
        )


        fields = [
            (
                "SYSTEM STATE",
                self.system_state_var
            ),
            (
                "FAULT DOMAIN",
                self.fault_var
            ),
            (
                "SEVERITY",
                self.severity_var
            ),
            (
                "ACTION",
                self.action_var
            ),
            (
                "SAFETY LATCH",
                self.latch_var
            ),
            (
                "ROBOT STATE",
                self.robot_var
            ),
            (
                "DIAGNOSTIC ENGINE",
                self.latency_var
            ),
        ]


        for row, (
            name,
            variable
        ) in enumerate(fields):

            ttk.Label(
                diagnostic_inner,
                text=name,
                font=("Segoe UI", 9, "bold")
            ).grid(
                row=row,
                column=0,
                sticky="w",
                pady=6
            )

            ttk.Label(
                diagnostic_inner,
                textvariable=variable,
                style="Status.TLabel"
            ).grid(
                row=row,
                column=1,
                sticky="w",
                padx=20,
                pady=6
            )


        # -------------------------------------------------
        # EVENT LOG
        # -------------------------------------------------

        log_frame = ttk.LabelFrame(
            middle,
            text=" Live Diagnostic Event Log ",
            style="Section.TLabelframe"
        )

        log_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(5, 0)
        )

        self.log_box = tk.Text(
            log_frame,
            font=("Consolas", 9),
            wrap="word",
            height=15
        )

        self.log_box.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )


        # -------------------------------------------------
        # FAULT INJECTION CONTROLS
        # -------------------------------------------------

        controls = ttk.LabelFrame(
            main,
            text=" Controlled Software Fault Injection ",
            style="Section.TLabelframe"
        )

        controls.pack(
            fill="x",
            pady=6
        )

        control_inner = ttk.Frame(
            controls,
            padding=8
        )

        control_inner.pack(
            fill="x"
        )


        buttons = [
            (
                "NORMAL RUN",
                self.normal_run
            ),
            (
                "THERMAL FAULT",
                self.thermal_fault
            ),
            (
                "SENSOR NOISE",
                self.sensor_fault
            ),
            (
                "POWER ANOMALY",
                self.power_fault
            ),
            (
                "COMM FAILURE",
                self.communication_fault
            ),
            (
                "TIMING FAULT",
                self.timing_fault
            ),
            (
                "RESET",
                self.reset_system
            ),
        ]


        for column, (
            text,
            command
        ) in enumerate(buttons):

            ttk.Button(
                control_inner,
                text=text,
                command=command,
                style="Demo.TButton"
            ).grid(
                row=0,
                column=column,
                padx=3,
                sticky="ew"
            )

            control_inner.columnconfigure(
                column,
                weight=1
            )


        # -------------------------------------------------
        # FOOTER
        # -------------------------------------------------

        ttk.Label(
            main,
            text=(
                "Evidence boundary: fault values are controlled "
                "software injections. Diagnostic timing shown is "
                "Python execution time on the development PC; "
                "it is not QNX, Arduino, physical-sensor, or "
                "certified safety-response latency."
            ),
            style="Subtitle.TLabel"
        ).pack(
            fill="x",
            pady=(4, 0)
        )


    # =====================================================
    # EVENT LOG
    # =====================================================

    def log(self, message):

        timestamp = time.strftime(
            "%H:%M:%S"
        )

        self.log_box.insert(
            "end",
            f"[{timestamp}] {message}\n"
        )

        self.log_box.see("end")


    # =====================================================
    # PIPELINE DISPLAY
    # =====================================================

    def clear_pipeline(self):

        for node in self.pipeline_nodes:
            node.configure(
                bg="#e8e8e8"
            )


    def pipeline_step(
        self,
        index,
        robot_state
    ):

        self.clear_pipeline()

        self.pipeline_nodes[
            index
        ].configure(
            bg="#fff2cc"
        )

        self.robot_var.set(
            robot_state
        )


    # =====================================================
    # HEALTH DISPLAY
    # =====================================================

    def update_health_display(
        self,
        results
    ):

        for result in results:

            label = self.health_labels.get(
                result.domain
            )

            if label is None:
                continue

            if result.status == "HEALTHY":

                background = "#d9ead3"

            elif result.status == "WARNING":

                background = "#fff2cc"

            else:

                if (
                    result.severity.value
                    == "CRITICAL"
                ):
                    background = "#f4cccc"
                else:
                    background = "#fce5cd"

            label.configure(
                text=(
                    f"{result.domain}\n"
                    f"{result.status}"
                ),
                bg=background
            )


    # =====================================================
    # DIAGNOSTIC EVALUATION
    # =====================================================

    def evaluate_current_state(
        self,
        source
    ):

        start_ns = time.perf_counter_ns()

        results = self.engine.evaluate_system(
            temperature_c=
                self.current_values[
                    "temperature"
                ],

            sensor_noise=
                self.current_values[
                    "sensor_noise"
                ],

            power_deviation_percent=
                self.current_values[
                    "power_deviation"
                ],

            communication_errors=
                self.current_values[
                    "communication_errors"
                ],

            control_execution_us=
                self.current_values[
                    "control_execution"
                ],
        )

        self.manager.evaluate(
            results
        )

        end_ns = time.perf_counter_ns()

        latency_us = (
            end_ns - start_ns
        ) / 1000.0


        self.update_health_display(
            results
        )


        # Find highest severity result

        severity_rank = {
            "INFO": 0,
            "WARNING": 1,
            "DEGRADED": 2,
            "CRITICAL": 3,
        }

        dominant = max(
            results,
            key=lambda item:
                severity_rank.get(
                    item.severity.value,
                    0
                )
        )


        self.system_state_var.set(
            self.manager.state.value
        )

        self.fault_var.set(
            dominant.domain
            if dominant.status != "HEALTHY"
            else "NONE"
        )

        self.severity_var.set(
            dominant.severity.value
        )

        self.action_var.set(
            dominant.action.value
        )

        self.latch_var.set(
            "LATCHED"
            if self.manager.safe_mode_latched
            else "CLEAR"
        )

        self.latency_var.set(
            f"{latency_us:.2f} us "
            "(PC Python)"
        )


        self.log(
            f"{source} | "
            f"state={self.manager.state.value} | "
            f"fault="
            f"{self.fault_var.get()} | "
            f"severity="
            f"{self.severity_var.get()} | "
            f"action="
            f"{self.action_var.get()}"
        )


        return results


    # =====================================================
    # NORMAL PIPELINE ANIMATION
    # =====================================================

    def normal_run(self):

        if self.running_sequence:
            return

        if self.manager.safe_mode_latched:

            self.log(
                "COMMAND BLOCKED: "
                "NORMAL RUN rejected because "
                "SAFE_MODE latch is active."
            )

            self.robot_var.set(
                "STOPPED"
            )

            return


        self.running_sequence = True

        self.current_values = dict(
            self.default_values
        )

        self.evaluate_current_state(
            "NORMAL RUN"
        )

        sequence = [
            (0, "READY", "Camera acquisition"),
            (1, "READY", "Vision processing"),
            (2, "READY", "QNX IPC transfer"),
            (3, "READY", "Real-time control decision"),
            (4, "COMPONENT_HELD", "Robot command interface"),
            (5, "MOVING", "Pick / Move / Place"),
        ]


        def execute_step(index):

            if index >= len(sequence):

                self.clear_pipeline()

                self.robot_var.set(
                    "READY"
                )

                self.log(
                    "NORMAL CYCLE COMPLETE | "
                    "Robot returned to READY."
                )

                self.running_sequence = False

                return


            node_index, state, message = (
                sequence[index]
            )

            self.pipeline_step(
                node_index,
                state
            )

            self.log(
                message
            )

            self.root.after(
                650,
                lambda:
                    execute_step(
                        index + 1
                    )
            )


        execute_step(0)


    # =====================================================
    # FAULT INJECTION
    # =====================================================

    def thermal_fault(self):

        self.current_values = dict(
            self.default_values
        )

        self.current_values[
            "temperature"
        ] = 82.0

        self.robot_var.set(
            "STOPPED"
        )

        self.evaluate_current_state(
            "INJECT THERMAL = 82 C"
        )

        self.log(
            "Critical thermal condition -> "
            "SAFE_MODE requested."
        )


    def sensor_fault(self):

        self.current_values = dict(
            self.default_values
        )

        self.current_values[
            "sensor_noise"
        ] = 18.0

        self.evaluate_current_state(
            "INJECT SENSOR NOISE = 18"
        )

        if not self.manager.safe_mode_latched:

            self.robot_var.set(
                "DEGRADED"
            )

        self.log(
            "Sensor degradation detected -> "
            "DEGRADED operation."
        )


    def power_fault(self):

        self.current_values = dict(
            self.default_values
        )

        self.current_values[
            "power_deviation"
        ] = 27.0

        self.robot_var.set(
            "STOPPED"
        )

        self.evaluate_current_state(
            "INJECT POWER DEVIATION = 27%"
        )

        self.log(
            "Critical power anomaly -> "
            "SAFE_MODE requested."
        )


    def communication_fault(self):

        self.current_values = dict(
            self.default_values
        )

        self.current_values[
            "communication_errors"
        ] = 5

        self.robot_var.set(
            "STOPPED"
        )

        self.evaluate_current_state(
            "INJECT COMM ERRORS = 5"
        )

        self.log(
            "Communication failure -> "
            "SAFE_MODE requested."
        )


    def timing_fault(self):

        self.current_values = dict(
            self.default_values
        )

        self.current_values[
            "control_execution"
        ] = 100000

        self.robot_var.set(
            "STOPPED"
        )

        self.evaluate_current_state(
            "INJECT CONTROL = 100000 us"
        )

        self.log(
            "Control deadline violation "
            "(prototype requirement 80000 us) "
            "-> SAFE_MODE requested."
        )


    # =====================================================
    # RESET
    # =====================================================

    def reset_system(self):

        self.current_values = dict(
            self.default_values
        )

        healthy_results = (
            self.engine.evaluate_system(
                temperature_c=
                    self.current_values[
                        "temperature"
                    ],

                sensor_noise=
                    self.current_values[
                        "sensor_noise"
                    ],

                power_deviation_percent=
                    self.current_values[
                        "power_deviation"
                    ],

                communication_errors=
                    self.current_values[
                        "communication_errors"
                    ],

                control_execution_us=
                    self.current_values[
                        "control_execution"
                    ],
            )
        )


        reset_success = (
            self.manager.reset(
                healthy_results
            )
        )


        if reset_success:

            self.clear_pipeline()

            self.robot_var.set(
                "READY"
            )

            self.log(
                "EXPLICIT RESET ACCEPTED | "
                "Safety latch cleared."
            )

            self.evaluate_current_state(
                "POST-RESET HEALTH CHECK"
            )

        else:

            self.log(
                "RESET REJECTED | "
                "Active fault remains."
            )


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = EdgeGuardDigitalTwin(
        root
    )

    root.mainloop()