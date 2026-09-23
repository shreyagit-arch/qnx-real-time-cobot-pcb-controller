#include "telemetry_interface.h"

void telemetry_init(BaileyTelemetry *data)
{
    if (data == 0)
        return;

    data->thermal_c = 0.0;
    data->sensor_metric = 0.0;
    data->power_deviation_percent = 0.0;
    data->communication_errors = 0;

    data->vision_latency_us = 0;
    data->ipc_latency_us = 0;
    data->control_latency_us = 0;
    data->e2e_latency_us = 0;

    data->safety_latched = 0;
}

int telemetry_publish(const BaileyTelemetry *data)
{
    if (data == 0)
        return -1;

    /*
     * Transport to BAILEY-RT is intentionally not implemented yet.
     * This function defines the integration boundary only.
     */
    return 0;
}
