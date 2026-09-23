#ifndef TELEMETRY_INTERFACE_H
#define TELEMETRY_INTERFACE_H

typedef struct
{
    double thermal_c;
    double sensor_metric;
    double power_deviation_percent;
    unsigned int communication_errors;

    unsigned long long vision_latency_us;
    unsigned long long ipc_latency_us;
    unsigned long long control_latency_us;
    unsigned long long e2e_latency_us;

    int safety_latched;
} BaileyTelemetry;

void telemetry_init(BaileyTelemetry *data);
int telemetry_publish(const BaileyTelemetry *data);

#endif
