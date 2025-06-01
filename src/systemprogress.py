
class SystemProgress(object):

    class SystemPosition(object):
        def __init__(self, x = 0, y = 0, z = 0) -> None:
            self.x = float(x)
            self.y = float(y)   
            self.z = float(z)

    """
    Represents the progress in a single system
    """
    system = ''
    earnings = 0.0
    controlling_power = ''
    power_play_state = ''
    power_play_state_control_progress = 0.0
    power_play_state_reinforcement = 0.0
    power_play_state_undermining = 0.0
    orig_power_play_state_control_progress = 0.0
    orig_power_play_state_reinforcement = 0.0
    orig_power_play_state_undermining = 0.0
    position = SystemPosition()