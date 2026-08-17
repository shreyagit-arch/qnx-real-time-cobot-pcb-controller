class Robot:

    def __init__(self):
        self.state = "READY"
        self.safety_latch = False

    def pick(self):

        if self.safety_latch:
            print("ROBOT : PICK BLOCKED - SAFETY LATCH ACTIVE")
            return False

        if self.state != "READY":
            print(
                f"ROBOT : PICK rejected "
                f"(current state: {self.state})"
            )
            return False

        self.state = "PICK"
        print("ROBOT : PICK")
        return True

    def move(self):

        if self.safety_latch:
            print("ROBOT : MOVE BLOCKED - SAFETY LATCH ACTIVE")
            return False

        if self.state != "PICK":
            print(
                f"ROBOT : MOVE rejected "
                f"(current state: {self.state})"
            )
            return False

        self.state = "MOVE"
        print("ROBOT : MOVE")
        return True

    def place(self):

        if self.safety_latch:
            print("ROBOT : PLACE BLOCKED - SAFETY LATCH ACTIVE")
            return False

        if self.state != "MOVE":
            print(
                f"ROBOT : PLACE rejected "
                f"(current state: {self.state})"
            )
            return False

        self.state = "PLACE"
        print("ROBOT : PLACE")
        return True

    def ready(self):

        if self.safety_latch:
            print("ROBOT : READY COMMAND BLOCKED")
            return False

        self.state = "READY"
        print("ROBOT : READY")
        return True

    def stop(self):

        self.state = "STOPPED"
        self.safety_latch = True

        print("ROBOT : STOPPED")

    def get_state(self):
        return self.state

    def is_latched(self):
        return self.safety_latch