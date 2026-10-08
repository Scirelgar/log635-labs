import glob
import os
import time
from datetime import datetime

import cv2

from Raspbot_Lib import Raspbot
from McLumk_Wheel_Sports import move_forward, rotate_left, rotate_right, stop_robot


NEAR_DISTANCE = 150
FAR_DISTANCE = 300
OBSTACLE_POLL_INTERVAL = 0.5

motion_speed = 32

bot = Raspbot()


def _init_systems():
    """Initialize the robot's systems."""
    bot.Ctrl_Ulatist_Switch(1) # Ultrasonic sensor
    time.sleep(0.1)

def _close_systems():
    """Close the robot's systems."""
    bot.Ctrl_Ulatist_Switch(0)
    bot.Ctrl_BEEP_Switch(0)
    bot.Ctrl_WQ2812_ALL(0,6)
    stop_robot(bot)
    time.sleep(0.1)


def read_ultrasonic_distance():
    """Read the distance reported by the ultrasonic sensor.

    Combine the high byte from register ``0x1B`` and the low byte from
    register ``0x1A``. For example, ``read_ultrasonic_distance()`` returns
    the current obstacle distance in millimetres.

    Returns:
        The measured distance in millimetres.
    """
    distance_high = int(bot.read_data_array(0x1B, 1)[0])
    distance_low = int(bot.read_data_array(0x1A, 1)[0])
    return (distance_high << 8) | distance_low


def sound_buzzer(times=1, duration=0.1, interval=0.1):
    """Sound the buzzer for a given duration in seconds.
    
    Uses the bot.Ctrl_BEEP_Switch attribute to control the buzzer state.

    Args:
        times: Number of times to sound the buzzer.
        duration: Time in seconds to keep the buzzer on.
        interval: Time in seconds between buzzer on and off states.
    """
    for _ in range(times):
        bot.Ctrl_BEEP_Switch(1)
        time.sleep(duration)
        bot.Ctrl_BEEP_Switch(0)
        time.sleep(interval)


def blink_leds(times=3, interval=0.2):
    """Blink the LEDs for a given number of times.
    
    Uses the bot.Ctrl_WQ2812_ALL attribute to control the
    LED state.

    Args:
        times: Number of times to blink the LEDs.
        interval: Time in seconds between LED on and off states.
    """
    for _ in range(times):
        bot.Ctrl_WQ2812_ALL(1, 6)
        time.sleep(interval)
        bot.Ctrl_WQ2812_ALL(0, 6)
        time.sleep(interval)


def open_camera():
    """Open the first video device that produces a frame.

    Probe numbered Linux video devices in order because Raspberry Pi 5 can
    expose processing devices alongside the USB camera. For example,
    ``camera, device = open_camera()`` opens a usable capture device.

    Returns:
        A ``(camera, device_path)`` pair, or ``(None, None)`` if no device
        can provide a frame. The caller must release a returned camera.
    """
    devices = [
        path for path in glob.glob("/dev/video*") if path[len("/dev/video") :].isdigit()
    ]
    devices.sort(key=lambda path: int(path[len("/dev/video") :]))
    for device in devices:
        camera = cv2.VideoCapture(device, cv2.CAP_V4L2)
        usable = False
        try:
            if camera.isOpened():
                ok, frame = camera.read()
                usable = ok and frame is not None
                if usable:
                    return camera, device
        finally:
            if not usable:
                camera.release()
    return None, None


def take_photos(count=1, interval=0.5, directory="photos-eqK"):
    """Capture JPEG photos with the first available USB camera.

    Save photos in a local directory and return only successfully written
    files. For example, ``take_photos(count=3, interval=1)`` captures three
    photos one second apart.

    Args:
        count: Number of photos to attempt.
        interval: Seconds to wait between captures.
        directory: Destination directory, created if needed.

    Returns:
        A list of saved JPEG file paths; empty if no camera is available.

    Raises:
        RuntimeError: No usable camera is found.
    """
    camera, device = open_camera()
    if camera is None:
        raise RuntimeError("No usable camera found.")

    print(f"Camera: {device}")
    files = []
    try:
        os.makedirs(directory, exist_ok=True)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        for index in range(count):
            ok, frame = camera.read()
            if not ok or frame is None:
                print(f"Error: photo {index + 1} could not be captured.")
            else:
                name = (
                    datetime.now().strftime("%Y%m%d_%H%M%S_%f") + f"_{index + 1:03}.jpg"
                )
                path = os.path.join(directory, name)
                if cv2.imwrite(path, frame):
                    files.append(path)
                    print(f"Photo saved: {path}")
                else:
                    print(f"Error: photo {index + 1} could not be saved to {path}.")

            if index < count - 1:
                time.sleep(interval)
    finally:
        camera.release()

    return files


def follow_black_line(motion_speed: int = 15):
    """Read the IR sensors and make one short line-following movement.

    Register 0x0a contains four active-low sensor bits. X2, X1, X3, and X4
    correspond to the outer-left, inner-left, inner-right, and outer-right
    sensors, respectively.
    The mapping for the four sensors is as follows:\n
    X2 X1 X3 X4\n
    |  |  |  |\n
    L1 L2 R1 R2\n
    L1: Left outermost sensor\n
    L2: Left inner sensor\n
    R1: Right inner sensor\n
    R2: Right outermost sensor\n

    Example: ```follow_black_line(30)``` reads and responds once.

    Args:
        motion_speed: Base speed sent to the movement helpers.
    """
    if not isinstance(motion_speed, int) or motion_speed < 0 or motion_speed > 100:
        raise ValueError("motion_speed must be an integer between 0 and 100.")
    track = int(bot.read_data_array(0x0A, 1)[0])
    line_l1 = (track >> 2) & 0x01
    line_l2 = (track >> 3) & 0x01
    line_r1 = (track >> 1) & 0x01
    line_r2 = track & 0x01

    # Analyze the sensor readings and determine the appropriate action
    if (
        line_l1 == line_l2 == line_r1 == line_r2 == 0
    ):  # All sensors on black, T junction for start
        decision = "1"
        movement, speed, duration = move_forward, motion_speed, 0.01
    elif (
        line_l2 == 0 or line_l1 == 0
    ) and line_r2 == 0:  # Left sensors on black, right sensor on white, turn right
        decision = "2"
        movement, speed, duration = rotate_right, int(motion_speed * 1.7), 0.05
    elif line_l1 == 0 and (
        line_r2 == 0 or line_r1 == 0
    ):  # Left sensor on white, right sensors on black, turn left
        decision = "3"
        movement, speed, duration = rotate_left, int(motion_speed * 1.7), 0.05
    elif line_l1 == 0:  # Left outer sensor on black, turn left
        decision = "4"
        movement, speed, duration = rotate_left, motion_speed, 0.03
    elif line_r2 == 0:  # Right outer sensor on black, turn right
        decision = "5"
        movement, speed, duration = rotate_right, motion_speed, 0.03
    elif (
        line_l2 == 0 and line_r1 == 1
    ):  # Left inner sensor on black, right inner sensor on white, rotate left
        decision = "6"
        movement, speed, duration = rotate_left, motion_speed, 0.03
    elif (
        line_l2 == 1 and line_r1 == 0
    ):  # Left inner sensor on white, right inner sensor on black, rotate right
        decision = "7"
        movement, speed, duration = rotate_right, motion_speed, 0.03
    elif line_l2 == 0 and line_r1 == 0:  # Both inner sensors on black, move forward
        decision = "8"
        movement, speed, duration = move_forward, motion_speed, 0.03
    else:
        decision = "Line lost"
        movement = None

    print(decision)
    print(line_l1, line_l2, line_r1, line_r2)
    if movement is None:
        stop_robot(bot)
    else:
        movement(speed, duration)
    time.sleep(0.01)

def main():
    try:
        _init_systems()
        while True:
            follow_black_line(motion_speed)

            distance = read_ultrasonic_distance()
            if distance > NEAR_DISTANCE:
                continue

            stop_robot(bot)
            sound_buzzer(times=2)

            try:
                photos = take_photos(count=1)
                if not photos:
                    print("Warning: obstacle photo could not be captured.")
            except RuntimeError as error:
                print(f"Warning: obstacle photo could not be captured: {error}")

            blink_leds(times=2)

            while read_ultrasonic_distance() < FAR_DISTANCE:
                sound_buzzer(times=3, duration=0.2, interval=0.2)
                time.sleep(OBSTACLE_POLL_INTERVAL)
    except KeyboardInterrupt:
        print("Ending")
    finally:
        _close_systems()

if __name__ == "__main__":
    main()
