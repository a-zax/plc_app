import socket
from umodbus.client import tcp
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp

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

    def is_connected(self):
        return self._connected


# ---------------- UI DESIGN (KV Language) ----------------
KV = """
ScreenManager:
    SplashScreen:
    MainScreen:

<SplashScreen>:
    name: "splash"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.1, 0.3, 0.6, 1
        spacing: "20dp"
        padding: "50dp"

        MDLabel:
            text: "PLC Controller"
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            halign: "center"
            font_style: "H4"

        MDLabel:
            text: "Loading..."
            halign: "center"
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 0.8

<MainScreen>:
    name: "main"
    MDBoxLayout:
        orientation: "vertical"
        spacing: "10dp"
        padding: "10dp"

        MDTopAppBar:
            title: "PLC Controller"
            elevation: 4

        MDCard:
            orientation: "horizontal"
            padding: "10dp"
            spacing: "10dp"
            size_hint_y: None
            height: "80dp"

            MDTextField:
                id: ip_input
                hint_text: "PLC IP"
                text: "192.168.0.104"
                mode: "rectangle"

            MDTextField:
                id: port_input
                hint_text: "Port"
                text: "502"
                mode: "rectangle"
                input_filter: "int"

            MDRaisedButton:
                id: connect_btn
                text: "Connect"
                md_bg_color: app.theme_cls.primary_color
                on_release: app.connect_plc()

        MDLabel:
            id: status
            text: "Not connected"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 1,0,0,1
            size_hint_y: None
            height: "40dp"

        # ----------- D-Pad Layout -----------
        MDBoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: "200dp"
            spacing: "10dp"

            # UP
            MDBoxLayout:
                spacing: "10dp"
                MDRaisedButton:
                    text: "UP"
                    size_hint_x: 0.4
                    pos_hint: {"center_x": 0.5}
                    on_release: app.send_cmd("%M601", 1)

            # LEFT + RIGHT
            MDBoxLayout:
                spacing: "10dp"
                MDRaisedButton:
                    text: "LEFT"
                    on_release: app.send_cmd("%M603", 1)
                MDRaisedButton:
                    text: "RIGHT"
                    on_release: app.send_cmd("%M604", 1)

            # DOWN
            MDBoxLayout:
                spacing: "10dp"
                MDRaisedButton:
                    text: "DOWN"
                    size_hint_x: 0.4
                    pos_hint: {"center_x": 0.5}
                    on_release: app.send_cmd("%M602", 1)

        # ----------- Other Controls -----------
        MDGridLayout:
            cols: 2
            spacing: "10dp"
            adaptive_height: True

            MDRaisedButton:
                text: "Valve Open"
                on_release: app.send_cmd("%M607", 1)

            MDRaisedButton:
                text: "Valve Close"
                on_release: app.send_cmd("%M608", 1)

            MDRaisedButton:
                text: "Jet"
                on_release: app.send_cmd("%M605", 1)

            MDRaisedButton:
                text: "Spray"
                on_release: app.send_cmd("%M606", 1)

            MDRaisedButton:
                text: "Foam"
                on_release: app.send_cmd("%M609", 1)

            MDRaisedButton:
                text: "Reset"
                on_release: app.send_cmd("%M610", 1)

            MDRaisedButton:
                text: "Timer Start"
                md_bg_color: 1, 0, 0, 1
                on_release: app.send_cmd("%M611", 1)
"""


# ---------------- MAIN APP ----------------
class SplashScreen(Screen):
    pass


class MainScreen(Screen):
    pass


class PLCApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.plc = None
        sm = Builder.load_string(KV)

        # Switch to main screen after 2 seconds
        Clock.schedule_once(lambda dt: setattr(sm, "current", "main"), 2)
        return sm

    def connect_plc(self):
        ip = self.root.get_screen("main").ids.ip_input.text.strip()
        port = int(self.root.get_screen("main").ids.port_input.text.strip())
        self.plc = PLCConnection(ip, port)

        status_label = self.root.get_screen("main").ids.status
        if self.plc.openPLC():
            status_label.text = f"Connected to {ip}:{port}"
            status_label.text_color = (0, 0.7, 0, 1)
        else:
            status_label.text = "Connection failed"
            status_label.text_color = (1, 0, 0, 1)

    def send_cmd(self, reg, val):
        status_label = self.root.get_screen("main").ids.status
        if self.plc and self.plc.is_connected():
            ok = self.plc.writePLC(reg, val)
            if ok:
                status_label.text = f"Sent {val} → {reg}"
                status_label.text_color = (0, 0.7, 0, 1)
            else:
                status_label.text = "Failed to send"
                status_label.text_color = (1, 0, 0, 1)
        else:
            status_label.text = "Not connected"
            status_label.text_color = (1, 0, 0, 1)


if __name__ == "__main__":
    PLCApp().run()
