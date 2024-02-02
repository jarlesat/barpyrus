import subprocess
import re
import barpyrus.colors
from barpyrus.core import EventInput
from barpyrus.widgets import Widget


class PactlFollow(EventInput):
    def __init__(self):
        super(PactlFollow, self).__init__("pactl subscribe")
        self.proc.stdin.close()
        self.callback = lambda line: self.update(line)
        self.muted = self.get_muted_state()
        self.volume = self.get_volume()

    def update(self, line):
        if "Event 'change' on sink " in line:
            self.muted = self.get_muted_state()
            self.volume = self.get_volume()

    def get_volume(self):
        try:
            # Run the shell command to get muted state
            result = subprocess.run(['pactl', 'get-sink-volume', '@DEFAULT_SINK@'], capture_output=True, text=True)

            # Check the command's return code to ensure it executed successfully
            if result.returncode == 0:
                output = result.stdout
                # Extract volume levels using regular expressions
                left_channel_match = re.search(r'Front Left: (.+)%', output)
                right_channel_match = re.search(r'Front Right: (.+)%', output)

                if left_channel_match and right_channel_match:
                    left_volume = int(left_channel_match.group(1))
                    right_volume = int(right_channel_match.group(1))

                    # Calculate and return the average volume
                    average_volume = (left_volume + right_volume) / 2
                    return average_volume
                else:
                    print("Volume levels not found in the output.")
                    return None
            else:
                print("Error executing the command.")
                return None
        except Exception as e:
            print("An error occurred:", e)
            return None

    def get_muted_state(self):
        try:
            # Run the shell command to get muted state
            result = subprocess.run(['pactl', 'get-sink-mute', '@DEFAULT_SINK@'], capture_output=True, text=True)

            # Check the command's return code to ensure it executed successfully
            if result.returncode == 0:
                output = result.stdout
                # Parse the output to find the mute status
                if "yes" in output:
                    return True  # Muted
                elif "no" in output:
                    return False  # Not muted
                else:
                    return None  # Mute state couldn't be determined
            else:
                print("Error executing the command.")
                return None
        except Exception as e:
            print("An error occurred:", e)
            return None


class Pactl(Widget):
    def __init__(self):
        super(Pactl, self).__init__()
        self.pactl = PactlFollow()

    def render(self, p):
        muted = self.pactl.muted
        if muted:
            p.fg(barpyrus.colors.YELLOW_LIGHT)
        else:
            p.fg(barpyrus.colors.GRAY_LIGHT)
        p.symbol(0xe202)

    def eventinputs(self):
        return [self.pactl]
