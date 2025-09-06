import time
import socket
from umodbus.client import tcp

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup


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

        s = address.lower()
        is_reg = s.startswith("%mw")

        if is_reg:
            _fn = tcp.write_single_register
            dst = int(s.strip("%mw"))
        else:
            _fn = tcp.write_single_coil
            dst = int(s.strip("%m"))
            value = 0xFF00 if value != 0 else 0x0000

        msg = _fn(slave_id=1, address=dst, value=value)
        try:
            tcp.send_message(msg, self.sock)
            return True
        except Exception as e:
            print(f"Write error: {e}")
            self._connected = False
            return False


# ---------------- MAIN UI ----------------
class PLCApp(App):
    def build(self):
        self.plc = None
        self.last_ip = "192.168.0.104"

        root = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Connection row
        conn_layout = BoxLayout(size_hint_y=0.2)
        self.ip_input = TextInput(text=self.last_ip, multiline=False, hint_text="PLC IP")
        self.port_input = TextInput(text="502", multiline=False, input_filter="int", hint_text="Port")
        self.conn_btn = Button(text="Connect", on_press=self.connect_plc)
        conn_layout.add_widget(self.ip_input)
        conn_layout.add_widget(self.port_input)
        conn_layout.add_widget(self.conn_btn)

        # Status
        self.status = Label(text="Not connected", size_hint_y=0.1)

        # Control buttons
        controls = BoxLayout(orientation="vertical", spacing=5)

        # First row
        row1 = BoxLayout()
        row1.add_widget(Button(text="⬆️ UP", on_press=lambda x: self.send_cmd("%M601", 1)))
        row1.add_widget(Button(text="⬇️ DOWN", on_press=lambda x: self.send_cmd("%M602", 1)))
        controls.add_widget(row1)

        # Second row
        row2 = BoxLayout()
        row2.add_widget(Button(text="⬅️ LEFT", on_press=lambda x: self.send_cmd("%M603", 1)))
        row2.add_widget(Button(text="➡️ RIGHT", on_press=lambda x: self.send_cmd("%M604", 1)))
        controls.add_widget(row2)

        # Third row
        row3 = BoxLayout()
        row3.add_widget(Button(text="Valve Open", on_press=lambda x: self.send_cmd("%M607", 1)))
        row3.add_widget(Button(text="Valve Close", on_press=lambda x: self.send_cmd("%M608", 1)))
        controls.add_widget(row3)

        # Fourth row
        row4 = BoxLayout()
        row4.add_widget(Button(text="Jet", on_press=lambda x: self.send_cmd("%M605", 1)))
        row4.add_widget(Button(text="Spray", on_press=lambda x: self.send_cmd("%M606", 1)))
        controls.add_widget(row4)

        # Fifth row
        row5 = BoxLayout()
        row5.add_widget(Button(text="Foam", on_press=lambda x: self.send_cmd("%M609", 1)))
        row5.add_widget(Button(text="Reset", on_press=lambda x: self.send_cmd("%M610", 1)))
        controls.add_widget(row5)

        # Timer row
        row6 = BoxLayout()
        row6.add_widget(Button(text="Timer Start", on_press=lambda x: self.send_cmd("%M611", 1)))
        controls.add_widget(row6)

        # Add everything
        root.add_widget(conn_layout)
        root.add_widget(self.status)
        root.add_widget(controls)

        return root

    def connect_plc(self, instance):
        ip = self.ip_input.text.strip()
        port = int(self.port_input.text.strip())
        self.plc = PLCConnection(ip, port)

        if self.plc.openPLC():
            self.status.text = f"Connected to {ip}:{port}"
        else:
            self.status.text = "Connection failed"

    def send_cmd(self, reg, val):
        if self.plc and self.plc.is_connected():
            ok = self.plc.writePLC(reg, val)
            if ok:
                self.status.text = f"Sent {val} → {reg}"
            else:
                self.status.text = "Failed to send"
        else:
            self.status.text = "Not connected"


if __name__ == "__main__":
    PLCApp().run()
