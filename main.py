
from UI_functions import MainWidget

from kivy.app import App

class VirtualNetrworkSimulatorApp(App):
    def build(self):
        return MainWidget()

# Run the app
if __name__ == '__main__':
    VirtualNetrworkSimulatorApp().run()
