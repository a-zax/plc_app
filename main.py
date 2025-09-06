from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
import socket


# ---------------- PLC CONNECTION CLASS ----------------
class PLCConnection:
    def __init__(self, plc_ip, plc_port=502):
        self.plc_ip = plc_ip
        self.plc_port = plc_port
        self.sock = None
        self._connected = False
        self.sock_timeout = 1.0

    def openPLC(self):
        try:
            self.sock = socket.create_connection((self.plc_ip, self.plc_port), timeout=self.sock_timeout)
            self._connected = True
            return True
        except Exception as e:
            print(f"PLC connection failed: {e}")
            self._connected = False
            return False

    def writePLC(self, address, value):
        if not self._connected:
            if not self.openPLC():
                return False
        try:
            msg = f"{address}:{value}".encode()
            self.sock.sendall(msg)
            return True
        except Exception as e:
            print(f"Write error: {e}")
            self._connected = False
            return False

    def is_connected(self):
        return self._connected


# ---------------- SCREENS ----------------
class SplashScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(lambda dt: setattr(self.manager, "current", "main"), 2)


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=15, spacing=15)

        # Title
        title = Label(text="RWM Controller", font_size=28, bold=True, size_hint_y=0.1)
        layout.add_widget(title)

        # Connection row
        conn_row = BoxLayout(size_hint_y=0.1, spacing=10)
        self.ip_input = TextInput(text="192.168.0.104", multiline=False, hint_text="PLC IP", size_hint_x=0.5)
        self.port_input = TextInput(text="502", multiline=False, input_filter="int", size_hint_x=0.3)
        self.connect_btn = Button(text="Connect", background_color=(0.2, 0.6, 1, 1), bold=True,
                                  on_press=self.connect_plc, size_hint_x=0.2)
        conn_row.add_widget(self.ip_input)
        conn_row.add_widget(self.port_input)
        conn_row.add_widget(self.connect_btn)

        # Status
        self.status = Label(text="Not connected", size_hint_y=0.05, font_size=16)

        # ----------- Controls Layout -----------
        controls = BoxLayout(orientation="vertical", spacing=10, size_hint_y=0.85)

        # --- D-Pad style ---
        dpad = GridLayout(cols=3, spacing=10, size_hint_y=0.25)
        dpad.add_widget(Widget())
        dpad.add_widget(Button(text="UP", size_hint=(1, 1), on_press=lambda x: self.send_cmd("%M601", 1)))
        dpad.add_widget(Widget())

        dpad.add_widget(Button(text="LEFT", size_hint=(1, 1), on_press=lambda x: self.send_cmd("%M603", 1)))
        dpad.add_widget(Widget())
        dpad.add_widget(Button(text="RIGHT", size_hint=(1, 1), on_press=lambda x: self.send_cmd("%M604", 1)))

        dpad.add_widget(Widget())
        dpad.add_widget(Button(text="DOWN", size_hint=(1, 1), on_press=lambda x: self.send_cmd("%M602", 1)))
        dpad.add_widget(Widget())

        # --- Action buttons in grid ---
        actions = GridLayout(cols=2, spacing=10, size_hint_y=0.5)
        actions.add_widget(Button(text="Valve Open", size_hint=(1, 1), on_press=lambda x: self.send_cmd("%M607", 1)))
        actions.add_widget(Button(text="Valve Close", size_hint=(1, 1), on_press=lambda x: self.send_cmd("%M608", 1)))

        actions.add_widget(Button(text="Jet", size_hint=(1, 1), on_press=lambda x: self.send_cmd("%M605", 1)))
        actions.add_widget(Button(text="Spray", size_hint=(1, 1), on_press=lambda x: self.send_cmd("%M606", 1)))

        actions.add_widget(Button(text="Foam", size_hint=(1, 1), on_press=lambda x: self.send_cmd("%M609", 1)))
        actions.add_widget(Button(text="Reset", size_hint=(1, 1), on_press=lambda x: self.send_cmd("%M610", 1)))

        # Timer button (full width)
        timer_btn = Button(text="Timer Start", background_color=(1, 0.3, 0.3, 1),
                           size_hint_y=None, height=50, on_press=lambda x: self.send_cmd("%M611", 1))

        # Add to layout
        controls.add_widget(dpad)
        controls.add_widget(actions)
        controls.add_widget(timer_btn)

        layout.add_widget(conn_row)
        layout.add_widget(self.status)
        layout.add_widget(controls)
        self.add_widget(layout)

    def connect_plc(self, instance):
        ip = self.ip_input.text.strip()
        port = int(self.port_input.text.strip())
        self.plc = PLCConnection(ip, port)

        if self.plc.openPLC():
            self.status.text = f"Connected to {ip}:{port}"
        else:
            self.status.text = "Connection failed"

    def send_cmd(self, reg, val):
        if hasattr(self, "plc") and self.plc.is_connected():
            ok = self.plc.writePLC(reg, val)
            if ok:
                self.status.text = f"Sent {val} → {reg}"
            else:
                self.status.text = "Failed to send"
        else:
            self.status.text = "Not connected"


# ---------------- APP ----------------
class PLCApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(MainScreen(name="main"))
        return sm


if __name__ == "__main__":
    PLCApp().run()
