
from MainPackage.Router.Router import Router

# Import required modules from Kivy
from kivy.app import App
from kivy.uix.label import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color
from kivy.uix.label import Label

import random

def gemerate_ipv4():
    return ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
    
class MyNetwork:
    items = []



class MainWidget(BoxLayout):
    item_type = ""
    def select_router(self,state):
        if state == "down":
            self.item_type = "Router"
        else:
            self.item_type = ""
    
    def select_end_device(self,state):
        if state == "down":
            self.item_type = "End Device" 
        else:
            self.item_type = ""

    def clear_network(self):
        network_widget = self.ids.network_widget
        network_widget.clear_widgets()
        MyNetwork.items = []
        print("Clear Network")      
    
    def on_network_widget_touch(self,*args,**kwargs):
        network_widget = self.ids.network_widget
        touch_x, touch_y = args[1].pos
        # if its out of bounds, return
        if touch_x < 0 or touch_x > network_widget.width or touch_y < 0 or touch_y > network_widget.height:
            return
        if args[1].button == "left":
            self.handle_left_click( pos=(touch_x, touch_y))
        elif args[1].button == "right":
            self.ids.router_button.state = "normal"
            self.ids.device_button.state = "normal"
            self.item_type = ""

    def on_widget_press_callback(self,instance,*args):
        pass
        # network_widget = self.ids.network_widget
        # here it needs conversion to global coords of the mouse event TODO
        # pos = args[0].pos
        # min_d = dp(100000)
        # min_i = -1

        # # if the right click is pressed remove the widget
        # if args[0].button == "right":
        #     for index in range(len(MyNetwork.items)):
        #         item_zip = MyNetwork.items[index]
        #         widget = item_zip["widget"]
        #         d = (widget.x - pos[0])**2 + (widget.y - pos[1])**2
        #         if d < min_d:
        #             min_d = d
        #             min_i = index
        #     if min_i == -1: return
        #     wrapper = MyNetwork.items[min_i]["widget"]
        #     network_widget.remove_widget(wrapper)

    def handle_left_click(self, pos):
        network_widget = self.ids.network_widget
        image = None
        size = dp(40)

        if self.item_type == "Router":
            # generate router
            router_ipv4 = gemerate_ipv4()
            interfaces = [gemerate_ipv4(), gemerate_ipv4()]
            router = Router(router_ipv4, interfaces)

            # create widget
            wrapper = BoxLayout(
                orientation='vertical',
                size_hint=(None, None),
                size=(dp(160), dp(160)),
                pos=(pos[0] - dp(160) / 2, pos[1] - dp(160) / 2),
                on_touch_down= lambda instance, args=(network_widget): self.on_widget_press_callback(instance,args)
            )

            image = Image(
                size_hint=(None, None),
                size=(size, size),
                source='icons/router.png',
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            label_ipv4 = Label(
                text=router_ipv4,
                font_size=dp(10),
                color=(0, 0, 0.8, 1),
                halign='center',
                valign='middle',
                size_hint=(None, None),
                size=(dp(160), dp(20)),
            )
            label_interfaces = []
            for interface in interfaces:
                label_interfaces.append(
                    Label(
                        text=interface,
                        font_size=dp(10),
                        color=(0.8, 0, 0, 1),
                        halign='center',
                        valign='middle',
                        size_hint=(None, None),
                        size=(dp(160), dp(20)),
                    )
                )
            
            wrapper.add_widget(image)
            wrapper.add_widget(label_ipv4)
            for label_interface in label_interfaces:
                wrapper.add_widget(label_interface)
            network_widget.add_widget(wrapper)

            # add router to network
            MyNetwork.items.append({"type":"router","pos":pos,"item":router, "widget":wrapper})
            return
        elif self.item_type == "End Device":
            # generate end device
            end_device_ipv4 = gemerate_ipv4()
            # end_device = EndDevice(end_device_ipv4)
            

            # create widget
            wrapper = BoxLayout(
                orientation='vertical',
                size_hint=(None, None),
                size=(dp(160), dp(80)),
                pos=(pos[0] - dp(160) / 2, pos[1] - dp(80) / 2)
            )
            image = Image(
                size_hint=(None, None),
                size=(size, size),
                source='icons/device.png',
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            label_ipv4 = Label(
                text=end_device_ipv4,
                font_size=dp(10),
                color=(0, 0, 0.8, 1),
                halign='center',
                valign='middle',
                size_hint=(None, None),
                size=(dp(160), dp(20)),
            )
            wrapper.add_widget(image)
            wrapper.add_widget(label_ipv4)
            network_widget.add_widget(wrapper)

            # add end device to network
            MyNetwork.items.append({"type":"end_device","pos":pos,"item":end_device_ipv4, "widget":wrapper})
            return

    def on_network_widget_grab(self, *args, **kwargs):
        if self.item_type != "": return

        mouse_motion_event = args[1]
        offset_x, offset_y = mouse_motion_event.opos
        x , y = mouse_motion_event.x , mouse_motion_event.y

        dx , dy = x - offset_x , y - offset_y

        network_widget = self.ids.network_widget
        network_widget.x = dx
        network_widget.y = dy

        for item_zip in MyNetwork.items:
            widget = item_zip["widget"]
            widget.x = item_zip["pos"][0] + dx
            widget.y = item_zip["pos"][1] + dy

    def on_network_widget_release(self, *args, **kwargs):
        if self.item_type != "": return

        mouse_motion_event = args[1]
        offset_x, offset_y = mouse_motion_event.opos
        x , y = mouse_motion_event.x , mouse_motion_event.y

        dx , dy = x - offset_x , y - offset_y
        if abs(dx**2 + dy**2) < 10:
            return

        for index in range(len(MyNetwork.items)):
            item_zip = MyNetwork.items[index]
            widget = item_zip["widget"]
            widget.x = item_zip["pos"][0] + dx
            widget.y = item_zip["pos"][1] + dy
            MyNetwork.items[index]["pos"] = (item_zip["pos"][0] + dx, item_zip["pos"][1] + dy)

    def zoom_in(self,*args):
        if self.item_type != "": return

        mouse_event = args[1]
        center = mouse_event.opos

        for index in range(len(MyNetwork.items)):
            item_zip = MyNetwork.items[index]
            widget = item_zip["widget"]
            widget.x = (item_zip["pos"][0] - center[0])*1.2 + center[0]
            widget.y = (item_zip["pos"][1] - center[1])*1.2 + center[1]

            MyNetwork.items[index]["pos"] = (widget.x,widget.y)

    def zoom_out(self,*args):
        if self.item_type != "": return


        mouse_event = args[1]
        center = mouse_event.opos

        for index in range(len(MyNetwork.items)):
            item_zip = MyNetwork.items[index]
            widget = item_zip["widget"]
            widget.x = (item_zip["pos"][0] - center[0])/1.2 + center[0]
            widget.y = (item_zip["pos"][1] - center[1])/1.2 + center[1]

            MyNetwork.items[index]["pos"] = (widget.x,widget.y)

    def run_network(self):
        print("Run Network")


class VirtualNetrworkSimulatorApp(App):
    def build(self):
        return MainWidget()

# Run the app
if __name__ == '__main__':
    VirtualNetrworkSimulatorApp().run()
