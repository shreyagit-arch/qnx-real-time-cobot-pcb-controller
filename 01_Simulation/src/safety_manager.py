class SafetyManager:

    def __init__(self):
        self.state = "NORMAL"
        self.safety_latch = False

    def request_stop(self, robot):

        print("SAFETY : STOP_REQUESTED")

        self.state = "STOP_REQUESTED"

        robot.stop()

        self.safety_latch = True

        print("SAFETY : LATCH ACTIVE")

    def is_latched(self):
        return self.safety_latch

    def block_commands(self, robot):

        if self.safety_latch:

            print("ROBOT : COMMAND BLOCKED")

            return True

        return False