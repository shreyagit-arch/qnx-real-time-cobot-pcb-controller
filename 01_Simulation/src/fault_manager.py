class FaultManager:

    def __init__(self):
        self.fault_active = False
        self.fault_type = None

    def detect(self, fault_type):
        self.fault_active = True
        self.fault_type = fault_type

        print(f"FAULT MANAGER : {fault_type} DETECTED")

    def report_fault(self, fault_type):
        self.detect(fault_type)

    def has_fault(self):
        return self.fault_active

    def get_fault(self):
        return self.fault_type