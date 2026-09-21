/* =========================================================
   BAILEY-RT
   QNX PCB INSPECTION + SELF-DIAGNOSING EDGE DIGITAL TWIN

   CURRENT EVIDENCE BOUNDARY:
   Health values currently originate from representative
   software inputs evaluated by the BAILEY-RT HealthEngine.

   FUTURE HARDWARE SOURCE:
   Raspberry Pi / QNX sensor and telemetry inputs.
========================================================= */

let currentState = null;
let animationRunning = false;
let toastTimer = null;


/* =========================================================
   CONTINUOUS SELF-MONITORING
========================================================= */

let selfMonitoringEnabled = true;
let selfMonitoringTimer = null;
let selfMonitoringBusy = false;

const SELF_MONITOR_INTERVAL_MS = 1500;


/*
   Tracks whether the SAFE MODE overlay has already been shown
   for the current latched SAFE_MODE event.

   This prevents the automatic 1.5-second monitoring cycle
   from repeatedly reopening the overlay.
*/

let safeModeOverlayShown = false;


/* =========================================================
   UTILITIES
========================================================= */

function byId(id) {
    return document.getElementById(id);
}


function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


function setText(id, value) {

    const element = byId(id);

    if (element) {
        element.textContent = value;
    }
}


async function api(url, options = {}) {

    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json"
        },
        ...options
    });

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }

    return await response.json();
}


function showToast(title, message) {

    const toast = byId("toast");

    if (!toast) return;

    setText("toast-title", title);
    setText("toast-message", message);

    toast.classList.add("show");

    clearTimeout(toastTimer);

    toastTimer = setTimeout(() => {
        toast.classList.remove("show");
    }, 2400);
}


function escapeHtml(value) {

    const element = document.createElement("div");

    element.textContent = String(value);

    return element.innerHTML;
}


/* =========================================================
   INITIALIZATION
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        try {

            resetApplicationVisual();

            await refreshState();
            await loadEvidence();

            /*
                BAILEY-RT begins continuous automatic
                evaluation of all five monitored domains.
            */

            startSelfMonitoring();

            showToast(
                "BAILEY-RT SELF-MONITORING ACTIVE",
                "Five health domains are being evaluated automatically."
            );

        } catch (error) {

            console.error(error);

            showToast(
                "CONNECTION ERROR",
                "BAILEY-RT backend could not be reached."
            );
        }
    }
);


/* =========================================================
   BACKEND STATE
========================================================= */

async function refreshState() {

    const state = await api("/api/state");

    updateDashboard(state);

    return state;
}


/* =========================================================
   AUTOMATIC SELF-MONITORING CYCLE
========================================================= */

async function runSelfMonitoringCycle() {

    /*
        Do not overlap requests.

        Automatic refresh also pauses while a presentation
        animation is running so that the monitoring loop
        cannot overwrite the visual demonstration sequence.
    */

    if (
        !selfMonitoringEnabled ||
        selfMonitoringBusy ||
        animationRunning
    ) {
        return;
    }

    selfMonitoringBusy = true;

    try {

        /*
            /api/state -> build_state() -> evaluate()

            The backend evaluates ALL FIVE domains:

            THERMAL
            SENSOR
            POWER
            COMMUNICATION
            TIMING
        */

        const state = await refreshState();

        document.body.classList.add(
            "self-monitoring-active"
        );

        document.body.classList.toggle(
            "self-monitoring-fault",
            state.fault_domain !== "NONE"
        );

    } catch (error) {

        console.error(
            "BAILEY-RT self-monitoring error:",
            error
        );

        document.body.classList.remove(
            "self-monitoring-active"
        );

    } finally {

        selfMonitoringBusy = false;
    }
}


/* =========================================================
   START SELF-MONITORING
========================================================= */

function startSelfMonitoring() {

    if (selfMonitoringTimer !== null) {
        return;
    }

    selfMonitoringEnabled = true;

    /*
        Evaluate immediately.
    */

    runSelfMonitoringCycle();

    /*
        Continue automatic evaluation.
    */

    selfMonitoringTimer = setInterval(
        runSelfMonitoringCycle,
        SELF_MONITOR_INTERVAL_MS
    );
}


/* =========================================================
   DASHBOARD UPDATE
========================================================= */

function updateDashboard(state) {

    currentState = state;

    setText(
        "system-state",
        state.system_state
    );

    setText(
        "robot-state",
        state.robot_state
    );

    setText(
        "robot-state-secondary",
        state.robot_state
    );

    setText(
        "fault-domain",
        state.fault_domain
    );

    setText(
        "severity",
        state.severity
    );

    setText(
        "action",
        state.action
    );

    setText(
        "safety-latch",
        state.safety_latch
    );

    setText(
        "command-status",
        state.command_status
    );

    setText(
        "operating-mode",
        state.system_state
    );

    setText(
        "decision-response-text",
        state.action
    );

    setText(
        "decision-domain",
        state.fault_domain
    );

    setText(
        "decision-severity",
        state.severity
    );

    setText(
        "decision-action",
        state.action
    );

    setText(
        "decision-safety-result",
        state.safe_mode_latched
            ? "COMMANDS BLOCKED"
            : "COMMANDS ENABLED"
    );

    updateOverallStatus(state);

    if (Array.isArray(state.health)) {

        state.health.forEach(result => {
            updateHealth(result);
        });
    }

    updateDecisionFlow(state);

    updateRobotVisual(
        state.robot_state
    );

    renderEvents(
        state.events
    );

    updateSafetyOverlay(
        state
    );
}


/* =========================================================
   OVERALL STATUS
========================================================= */

function updateOverallStatus(state) {

    const status =
        byId("overall-status");

    if (!status) return;

    const dot =
        document.querySelector(
            ".status-dot"
        );

    if (
        state.system_state === "SAFE_MODE"
    ) {

        status.textContent =
            "SAFE MODE";

        status.style.color =
            "var(--red)";

        if (dot) {

            dot.style.background =
                "var(--red)";

            dot.style.boxShadow =
                "0 0 0 4px var(--red-soft)";
        }

    } else if (
        state.system_state === "DEGRADED"
    ) {

        status.textContent =
            "DEGRADED";

        status.style.color =
            "var(--amber)";

        if (dot) {

            dot.style.background =
                "var(--amber)";

            dot.style.boxShadow =
                "0 0 0 4px var(--amber-soft)";
        }

    } else {

        status.textContent =
            "HEALTHY";

        status.style.color =
            "var(--green)";

        if (dot) {

            dot.style.background =
                "var(--green)";

            dot.style.boxShadow =
                "0 0 0 4px var(--green-soft)";
        }
    }
}


/* =========================================================
   HEALTH MONITORING
========================================================= */

function updateHealth(result) {

    const card =
        byId(
            `health-${result.domain}`
        );

    const value =
        byId(
            `value-${result.domain}`
        );

    const status =
        byId(
            `status-${result.domain}`
        );

    const meter =
        byId(
            `meter-${result.domain}`
        );

    if (
        !card ||
        !value ||
        !status ||
        !meter
    ) {
        return;
    }


    /*
        COMMUNICATION and TIMING are displayed as integers.

        Other representative values retain one decimal place.
    */

    if (
        result.domain === "COMMUNICATION" ||
        result.domain === "TIMING"
    ) {

        value.textContent =
            Math.round(
                Number(
                    result.measured_value
                )
            );

    } else {

        value.textContent =
            Number(
                result.measured_value
            ).toFixed(1);
    }


    status.textContent =
        result.status;


    card.classList.remove(
        "healthy",
        "warning",
        "degraded",
        "fault"
    );


    if (
        result.status === "HEALTHY"
    ) {

        card.classList.add(
            "healthy"
        );

        meter.style.background =
            "var(--green)";

    } else if (
        result.status === "WARNING"
    ) {

        card.classList.add(
            "warning"
        );

        meter.style.background =
            "var(--amber)";

    } else if (
        result.severity === "DEGRADED"
    ) {

        card.classList.add(
            "degraded"
        );

        meter.style.background =
            "var(--amber)";

    } else {

        card.classList.add(
            "fault"
        );

        meter.style.background =
            "var(--red)";
    }


    meter.style.width =
        `${Math.max(
            4,
            Math.min(
                100,
                Number(
                    result.diagnostic_score
                )
            )
        )}%`;
}


/* =========================================================
   DIAGNOSTIC DECISION PATH
========================================================= */

function updateDecisionFlow(state) {

    const health =
        byId("decision-health");

    const fault =
        byId("decision-fault");

    const safety =
        byId("decision-safety");

    const response =
        byId("decision-response");


    [
        health,
        fault,
        safety,
        response
    ]
        .filter(Boolean)
        .forEach(node => {

            node.classList.remove(
                "active",
                "degraded",
                "critical"
            );
        });


    /*
        Health Engine remains active because
        continuous self-monitoring is running.
    */

    if (health) {

        health.classList.add(
            "active"
        );
    }


    if (
        state.fault_domain !== "NONE" &&
        fault
    ) {

        fault.classList.add(
            state.system_state === "SAFE_MODE"
                ? "critical"
                : "degraded"
        );
    }


    if (
        state.safe_mode_latched
    ) {

        if (safety) {

            safety.classList.add(
                "critical"
            );
        }

        if (response) {

            response.classList.add(
                "critical"
            );
        }

    } else if (
        state.system_state === "DEGRADED"
    ) {

        if (response) {

            response.classList.add(
                "degraded"
            );
        }
    }
}


/* =========================================================
   ROBOT VISUAL
========================================================= */

function updateRobotVisual(
    robotState
) {

    const robot =
        byId("robot");

    if (!robot) return;


    robot.classList.remove(
        "picking",
        "moving",
        "placing",
        "stopped",
        "degraded"
    );


    switch (robotState) {

        case "COMPONENT_HELD":

            robot.classList.add(
                "picking"
            );

            break;


        case "MOVING":

            robot.classList.add(
                "moving"
            );

            break;


        case "AT_DESTINATION":

            robot.classList.add(
                "placing"
            );

            break;


        case "STOPPED":

            robot.classList.add(
                "stopped"
            );

            break;


        case "DEGRADED":

            robot.classList.add(
                "degraded"
            );

            break;
    }
}


/* =========================================================
   APPLICATION VISUALS
========================================================= */

function resetApplicationVisual() {

    clearPipeline();

    setText(
        "vision-result",
        "STANDBY"
    );

    setText(
        "workcell-message",
        "SELF-MONITORING ACTIVE — PCB INSPECTION STANDBY"
    );


    const scanLine =
        byId("scan-line");

    if (scanLine) {

        scanLine.classList.remove(
            "running"
        );
    }


    document
        .querySelectorAll(
            ".qnx-module"
        )
        .forEach(module => {

            module.classList.remove(
                "active"
            );
        });
}


function startScan() {

    const scanLine =
        byId("scan-line");

    if (scanLine) {

        scanLine.classList.add(
            "running"
        );
    }
}


function stopScan() {

    const scanLine =
        byId("scan-line");

    if (scanLine) {

        scanLine.classList.remove(
            "running"
        );
    }
}


function setQnxModule(id) {

    document
        .querySelectorAll(
            ".qnx-module"
        )
        .forEach(module => {

            module.classList.remove(
                "active"
            );
        });


    const module =
        byId(id);

    if (module) {

        module.classList.add(
            "active"
        );
    }
}


/* =========================================================
   PIPELINE
========================================================= */

function clearPipeline() {

    document
        .querySelectorAll(
            ".pipeline-node"
        )
        .forEach(node => {

            node.classList.remove(
                "active",
                "complete"
            );
        });
}


function activatePipelineStage(stage) {

    document
        .querySelectorAll(
            ".pipeline-node"
        )
        .forEach(
            (node, index) => {

                node.classList.remove(
                    "active"
                );

                if (
                    index < stage
                ) {

                    node.classList.add(
                        "complete"
                    );

                } else if (
                    index === stage
                ) {

                    node.classList.add(
                        "active"
                    );
                }
            }
        );
}


function completePipeline() {

    document
        .querySelectorAll(
            ".pipeline-node"
        )
        .forEach(node => {

            node.classList.remove(
                "active"
            );

            node.classList.add(
                "complete"
            );
        });
}


/* =========================================================
   ROBOT STATE API
========================================================= */

async function setRobotState(state) {

    const result =
        await api(
            "/api/robot-state",
            {
                method: "POST",

                body: JSON.stringify({
                    state: state
                })
            }
        );


    if (result.state) {

        updateDashboard(
            result.state
        );
    }


    if (
        result.blocked ||
        result.success === false
    ) {
        return false;
    }


    return true;
}


/* =========================================================
   NORMAL PCB INSPECTION
========================================================= */

async function normalRun() {

    if (animationRunning) {

        showToast(
            "CYCLE ACTIVE",
            "An inspection cycle is already running."
        );

        return;
    }


    try {

        const state =
            await api(
                "/api/normal-run",
                {
                    method: "POST"
                }
            );


        updateDashboard(
            state
        );


        if (
            state.accepted === false
        ) {

            setText(
                "workcell-message",
                "COMMAND BLOCKED — SAFETY LATCH ACTIVE"
            );

            showToast(
                "COMMAND BLOCKED",
                "RESET is required before another cycle."
            );

            return;
        }


        animationRunning = true;

        resetApplicationVisual();


        /* CAMERA */

        activatePipelineStage(0);

        setText(
            "workcell-message",
            "CAMERA — ACQUIRING PCB IMAGE"
        );

        startScan();

        await sleep(900);


        /* VISION */

        activatePipelineStage(1);

        setQnxModule(
            "pipeline-vision"
        );

        setText(
            "vision-result",
            "INSPECTING"
        );

        setText(
            "workcell-message",
            "VISION TASK — INSPECTING PCB CONDITION"
        );

        await sleep(1100);

        stopScan();

        setText(
            "vision-result",
            "PASS"
        );

        await sleep(500);


        /* IPC */

        activatePipelineStage(2);

        setQnxModule(
            "pipeline-ipc"
        );

        setText(
            "workcell-message",
            "QNX IPC — TRANSFERRING INSPECTION RESULT"
        );

        await sleep(800);


        /* CONTROL */

        activatePipelineStage(3);

        setQnxModule(
            "pipeline-control"
        );

        setText(
            "workcell-message",
            "CONTROL TASK — PASS RESULT ACCEPTED"
        );

        await sleep(800);


        /* ROBOT INTERFACE */

        activatePipelineStage(4);

        setText(
            "workcell-message",
            "ROBOT INTERFACE — HANDLING COMMAND ISSUED"
        );


        let allowed =
            await setRobotState(
                "COMPONENT_HELD"
            );


        if (!allowed) {

            animationRunning = false;

            return;
        }


        await sleep(750);


        /* ROBOT MOVE */

        activatePipelineStage(5);

        setText(
            "workcell-message",
            "ROBOT — EXECUTING ACCEPTED WORKPIECE HANDLING"
        );


        allowed =
            await setRobotState(
                "MOVING"
            );


        if (!allowed) {

            animationRunning = false;

            return;
        }


        await sleep(850);


        /* DESTINATION */

        allowed =
            await setRobotState(
                "AT_DESTINATION"
            );


        if (!allowed) {

            animationRunning = false;

            return;
        }


        setText(
            "workcell-message",
            "PASS WORKPIECE — HANDLING DESTINATION REACHED"
        );

        await sleep(750);


        /* READY */

        await setRobotState(
            "READY"
        );


        completePipeline();

        setQnxModule("");


        setText(
            "workcell-message",
            "INSPECTION PASS — CYCLE COMPLETE / ROBOT READY"
        );


        showToast(
            "INSPECTION PASS",
            "Vision → IPC → Control → Robot cycle completed."
        );


        await sleep(1000);


        clearPipeline();

        animationRunning = false;


    } catch (error) {

        console.error(error);

        animationRunning = false;


        showToast(
            "ERROR",
            "Normal inspection cycle failed."
        );
    }
}


/* =========================================================
   CONTROLLED FAULT INJECTION

   IMPORTANT:
   These controls introduce abnormal representative software
   inputs. BAILEY-RT HealthEngine evaluates those inputs.

   They are demonstration/test controls, NOT physical sensors.
========================================================= */

async function injectFault(
    faultType
) {

    if (animationRunning) {

        showToast(
            "CYCLE ACTIVE",
            "Allow the current inspection cycle to finish."
        );

        return;
    }


    animationRunning = true;


    try {

        clearPipeline();

        stopScan();


        const scenarioNames = {

            sensor:
                "SENSOR",

            thermal:
                "THERMAL",

            power:
                "POWER",

            communication:
                "COMMUNICATION",

            timing:
                "TIMING"
        };


        const requestedDomain =
            scenarioNames[faultType] ||
            String(
                faultType
            ).toUpperCase();


        /* MONITORED INPUT */

        setText(
            "workcell-message",
            `${requestedDomain} MONITOR — ACQUIRING HEALTH INPUT`
        );


        showToast(
            "CONTROLLED FAULT INJECTION",
            `${requestedDomain} abnormal input introduced for self-monitoring test.`
        );


        const requestedCard =
            byId(
                `health-${requestedDomain}`
            );


        if (requestedCard) {

            requestedCard.classList.add(
                "diagnostic-focus"
            );
        }


        await sleep(900);


        /* INTRODUCE CONTROLLED INPUT */

        const state =
            await api(
                `/api/inject/${faultType}`,
                {
                    method: "POST"
                }
            );


        /* HEALTH ENGINE */

        setText(
            "workcell-message",
            `${state.fault_domain} — SELF-MONITORING DETECTED ABNORMAL INPUT`
        );


        const healthNode =
            byId(
                "decision-health"
            );


        if (healthNode) {

            healthNode.classList.add(
                "diagnostic-pulse"
            );
        }


        await sleep(900);


        /* DISPLAY RESULT */

        updateDashboard(
            state
        );


        setText(
            "workcell-message",
            `${state.fault_domain} — HEALTH CONDITION IDENTIFIED`
        );


        await sleep(1000);


        /* FAULT MANAGER */

        const faultNode =
            byId(
                "decision-fault"
            );


        if (healthNode) {

            healthNode.classList.remove(
                "diagnostic-pulse"
            );
        }


        if (faultNode) {

            faultNode.classList.add(
                "diagnostic-pulse"
            );
        }


        setText(
            "workcell-message",
            `${state.fault_domain} — FAULT MANAGER CLASSIFYING EVENT`
        );


        await sleep(900);


        /* SAFETY / RESPONSE */

        if (faultNode) {

            faultNode.classList.remove(
                "diagnostic-pulse"
            );
        }


        const safetyNode =
            byId(
                "decision-safety"
            );

        const responseNode =
            byId(
                "decision-response"
            );


        if (
            state.system_state ===
            "SAFE_MODE"
        ) {

            if (safetyNode) {

                safetyNode.classList.add(
                    "diagnostic-pulse"
                );
            }


            setText(
                "workcell-message",
                `${state.fault_domain} — SAFETY MANAGER EVALUATING CRITICAL FAULT`
            );


            await sleep(900);


            if (safetyNode) {

                safetyNode.classList.remove(
                    "diagnostic-pulse"
                );
            }


            if (responseNode) {

                responseNode.classList.add(
                    "diagnostic-pulse"
                );
            }


            setText(
                "workcell-message",
                `${state.fault_domain} FAULT — SAFE MODE / COMMANDS BLOCKED`
            );


            showToast(
                "CRITICAL HEALTH FAULT",
                `${state.fault_domain} → SAFE MODE`
            );


        } else if (
            state.system_state ===
            "DEGRADED"
        ) {

            if (responseNode) {

                responseNode.classList.add(
                    "diagnostic-pulse"
                );
            }


            setText(
                "workcell-message",
                `${state.fault_domain} DEGRADATION — DEGRADED RESPONSE SELECTED`
            );


            showToast(
                "DEGRADED MODE",
                `${state.fault_domain} degradation detected.`
            );


        } else {

            if (responseNode) {

                responseNode.classList.add(
                    "diagnostic-pulse"
                );
            }


            setText(
                "workcell-message",
                `${state.fault_domain} — DIAGNOSTIC EVENT LOGGED`
            );
        }


        await sleep(1100);


        /* FINAL DISPLAY */

        if (responseNode) {

            responseNode.classList.remove(
                "diagnostic-pulse"
            );
        }


        if (requestedCard) {

            requestedCard.classList.remove(
                "diagnostic-focus"
            );
        }


        animationRunning = false;


    } catch (error) {

        console.error(error);


        document
            .querySelectorAll(
                ".diagnostic-pulse, .diagnostic-focus"
            )
            .forEach(element => {

                element.classList.remove(
                    "diagnostic-pulse",
                    "diagnostic-focus"
                );
            });


        animationRunning = false;


        showToast(
            "ERROR",
            "Fault injection failed."
        );
    }
}


/* =========================================================
   RESET
========================================================= */

async function resetSystem() {

    if (animationRunning) {

        showToast(
            "CYCLE ACTIVE",
            "Allow the current cycle to finish."
        );

        return;
    }


    try {

        const state =
            await api(
                "/api/reset",
                {
                    method: "POST"
                }
            );


        /*
            The backend has processed RESET.

            updateDashboard() also calls updateSafetyOverlay().
            When the returned state is no longer latched,
            updateSafetyOverlay() rearms the overlay for the
            next future SAFE_MODE transition.
        */

        updateDashboard(
            state
        );


        if (
            state.reset_success
        ) {

            resetApplicationVisual();


            showToast(
                "RESET ACCEPTED",
                "Safety latch cleared. Self-monitoring continues."
            );

        } else {

            showToast(
                "RESET REJECTED",
                "An active fault remains."
            );
        }


    } catch (error) {

        console.error(error);


        showToast(
            "ERROR",
            "Reset request failed."
        );
    }
}


/* =========================================================
   SAFE MODE OVERLAY

   TRANSITION-BASED DISPLAY:

   NORMAL / DEGRADED -> SAFE_MODE
       Show overlay once.

   SAFE_MODE -> SAFE_MODE
       Do not reopen it during automatic monitoring.

   SAFE_MODE -> RESET / NORMAL
       Rearm overlay for the next critical event.
========================================================= */

function updateSafetyOverlay(state) {

    const overlay =
        byId(
            "safe-overlay"
        );


    if (!overlay) {
        return;
    }


    /*
        CRITICAL STATE / SAFE MODE LATCHED
    */

    if (
        state.safe_mode_latched
    ) {

        /*
            The overlay was already shown for this
            SAFE_MODE event.

            Automatic monitoring may continue refreshing
            the state every 1.5 seconds, but the popup
            must not reopen.
        */

        if (
            safeModeOverlayShown
        ) {
            return;
        }


        /*
            First observation of the current SAFE_MODE
            transition.
        */

        safeModeOverlayShown = true;


        setText(
            "safe-overlay-reason",
            `${state.fault_domain} fault detected by BAILEY-RT self-monitoring.`
        );


        overlay.classList.remove(
            "hidden"
        );


        /*
            Hide the visual popup after 1.7 seconds.

            IMPORTANT:
            safeModeOverlayShown remains TRUE while the
            safety latch remains active.
        */

        setTimeout(
            () => {

                overlay.classList.add(
                    "hidden"
                );

            },
            1700
        );


        return;
    }


    /*
        NOT IN SAFE MODE.

        Ensure the overlay is hidden and rearm it so that
        a future critical fault can display it again.
    */

    overlay.classList.add(
        "hidden"
    );

    safeModeOverlayShown = false;
}


/* =========================================================
   EVENTS
========================================================= */

function renderEvents(events) {

    const container =
        byId(
            "event-log"
        );


    if (!container) {
        return;
    }


    container.innerHTML = "";


    if (
        !events ||
        events.length === 0
    ) {

        container.innerHTML =
            `<div class="event-line">
                No diagnostic events recorded.
             </div>`;

        return;
    }


    events.forEach(event => {

        const line =
            document.createElement(
                "div"
            );


        const level =
            String(
                event.level || "info"
            ).toLowerCase();


        line.className =
            `event-line ${level}`;


        const message =
            String(
                event.message
            ).replaceAll(
                "EdgeGuard",
                "BAILEY-RT"
            );


        line.innerHTML =
            `<strong>${escapeHtml(
                event.timestamp
            )}</strong>
             ${escapeHtml(
                message
            )}`;


        container.appendChild(
            line
        );
    });
}


/* =========================================================
   CLEAR EVENTS
========================================================= */

async function clearEventLog() {

    try {

        const state =
            await api(
                "/api/clear-log",
                {
                    method: "POST"
                }
            );


        updateDashboard(
            state
        );


        showToast(
            "EVENT LOG",
            "Diagnostic event stream cleared."
        );


    } catch (error) {

        console.error(error);
    }
}


/* =========================================================
   CSV EXPERIMENTAL EVIDENCE
========================================================= */

async function loadEvidence() {

    try {

        const evidence =
            await api(
                "/api/evidence"
            );


        if (
            !evidence.available
        ) {

            setText(
                "evidence-trials",
                "N/A"
            );

            setText(
                "evidence-correct",
                "N/A"
            );

            setText(
                "evidence-rate",
                "N/A"
            );

            return;
        }


        setText(
            "evidence-trials",
            evidence.total_trials
        );


        setText(
            "evidence-correct",
            `${evidence.correct_responses}/${evidence.total_trials}`
        );


        setText(
            "evidence-rate",
            `${Number(
                evidence.overall_rate_percent
            ).toFixed(2)}%`
        );


        const body =
            byId(
                "evidence-body"
            );


        if (!body) {
            return;
        }


        body.innerHTML = "";


        evidence.experiments.forEach(
            experiment => {

                const row =
                    document.createElement(
                        "tr"
                    );


                row.innerHTML = `
                    <td>
                        ${escapeHtml(
                            experiment.experiment_id
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            experiment.domain
                        )}
                    </td>

                    <td>
                        ${experiment.trials}
                    </td>

                    <td>
                        ${experiment.correct_detections}
                        /
                        ${experiment.trials}
                    </td>

                    <td>
                        ${Number(
                            experiment.mean_latency_us
                        ).toFixed(2)}
                        µs
                    </td>

                    <td>
                        ${escapeHtml(
                            experiment.observed_state
                        )}
                    </td>
                `;


                body.appendChild(
                    row
                );
            }
        );


    } catch (error) {

        console.error(
            "Evidence loading failed:",
            error
        );
    }
}