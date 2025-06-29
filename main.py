from pynput import mouse, keyboard
import time
import threading


def sign(value: int) -> int:
    """Returns the sign of the value: -1 for negative, 1 for positive, 0 for zero."""
    return (value > 0) - (value < 0)


class AxisController:
    def __init__(self, negative_key: str, positive_key: str, off_delay: float, enabled: bool = False):
        self.negative_key = negative_key
        self.positive_key = positive_key
        self.off_delay = off_delay

        self.enabled = enabled
        self.keyboard = keyboard.Controller()
        self.prev = None
        self.controller_state = 0
        self.last_press_time = 0

    def set_value(self, value: int | None):
        self.prev = value

    def move(self, value: int | None):
        if value is None:
            value = self.prev
            delta = 0
        else:
            if self.prev is None:
                delta = 0
            else:
                delta = value - self.prev
            self.prev = value
        if not self.enabled:
            delta = 0

        new_state = sign(delta)
        current_time = time.time()
        if new_state != 0:
            self.last_press_time = current_time
            if self.controller_state * new_state < 0:
                self._release_keys()
            if self.controller_state != new_state:
                self._press_key(new_state)

        if current_time - self.last_press_time > self.off_delay:
            self._release_keys()

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        if not enabled:
            self._release_keys()

    def _release_keys(self):
        if self.controller_state < 0:
            self.keyboard.release(self.negative_key)
        elif self.controller_state > 0:
            self.keyboard.release(self.positive_key)
        self.controller_state = 0

    def _press_key(self, new_state: int):
        if new_state < 0:
            self.keyboard.press(self.negative_key)
        elif new_state > 0:
            self.keyboard.press(self.positive_key)
        self.controller_state = new_state


class SDVXMouseController(mouse.Listener):
    def __init__(self, x_negative: str = 'a', x_positive: str = 's', y_negative: str = 'l', y_positive: str = ';',
                 off_delay: float = 0.01):
        self.mouse_listener = mouse.Listener(on_move=self.move)
        self.mouse = mouse.Controller()
        self.keyboard_listener = keyboard.GlobalHotKeys({
            '<ctrl>+<f12>': self.toggle_enabled,
            '<ctrl>+c': self.stop,
        })
        self.enabled = False
        self.off_delay = off_delay
        self.axis_x = AxisController(x_negative, x_positive, off_delay)
        self.axis_y = AxisController(y_negative, y_positive, off_delay)
        self._periodic_thread = None
        self._periodic_stop = threading.Event()

    def move(self, dx, dy):
        self.axis_x.move(dx)
        self.axis_y.move(dy)

    def toggle_enabled(self):
        self.enabled = not self.enabled
        self.axis_x.set_enabled(self.enabled)
        self.axis_y.set_enabled(self.enabled)
        if self.enabled:
            print("変換を開始しました / Conversion started.")
        else:
            print("変換を停止しました / Conversion stopped")

    def __enter__(self) -> 'SDVXMouseController':
        self.start()
        return self

    def start(self):
        self.mouse_listener.start()
        self.keyboard_listener.start()
        self._periodic_stop.clear()

        def periodic_move():
            while not self._periodic_stop.is_set():
                try:
                    self.move(None, None)
                    if self.enabled:
                        # Reset the mouse position to center
                        self.axis_x.set_value(300)
                        self.axis_y.set_value(300)
                        self.mouse.position = (300, 300)
                    time.sleep(self.off_delay / 2)
                except KeyboardInterrupt:
                    # ignore KeyboardInterrupt in the thread
                    continue
        self._periodic_thread = threading.Thread(
            target=periodic_move, daemon=True
        )
        self._periodic_thread.start()

    def stop(self):
        self._periodic_stop.set()
        if self._periodic_thread is not None:
            self._periodic_thread.join(timeout=1)
            self._periodic_thread = None
        self.mouse_listener.stop()
        self.keyboard_listener.stop()

    def join(self):
        self.mouse_listener.join()
        self.keyboard_listener.join()
        self._periodic_stop.set()
        if self._periodic_thread is not None:
            self._periodic_thread.join(timeout=1)


def main():
    import json
    from pathlib import Path

    config_path = Path(__file__).parent / 'config.json'
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {
            "x_negative": "a",
            "x_positive": "s",
            "y_negative": "l",
            "y_positive": ";",
            "off_delay": 0.01
        }
    print("Ctrl+F12 で変換開始/停止 / Press Ctrl+F12 to start/stop conversion")
    print("Ctrl+C で終了 / Press Ctrl+C to terminate")
    with SDVXMouseController(**config) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            listener.stop()


if __name__ == "__main__":
    main()
