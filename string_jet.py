class StringJetPlane:
    """String-jet style plane.

    Engaging the plane opens the interlock, and an open interlock
    accessalizes travel for the viewing system.
    """

    def __init__(self):
        self.style = "string-jet"
        self.engaged = False
        self.interlock_open = False
        self.travel_accessalized = False

    def engage(self):
        """Engage the plane: open the interlock and accessalize travel."""
        self.engaged = True
        self.interlock_open = True
        self.travel_accessalized = True
        return self.get_state()

    def disengage(self):
        """Disengage the plane: close the interlock and secure travel."""
        self.engaged = False
        self.interlock_open = False
        self.travel_accessalized = False
        return self.get_state()

    def get_state(self):
        """Return string-jet plane state."""
        return {
            "style": self.style,
            "engaged": self.engaged,
            "interlock_open": self.interlock_open,
            "travel_accessalized": self.travel_accessalized,
        }


string_jet_plane = StringJetPlane()
