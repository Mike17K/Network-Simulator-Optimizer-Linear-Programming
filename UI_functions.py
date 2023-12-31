
from MainPackage.Router.Router import Router
from MainPackage.Interface.Interface import Interface
from MainPackage.Packet.Packet import Packet

from analyzeExportConnections import solve

# Import required modules from Kivy
from kivy.uix.label import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color, Line
from kivy.uix.label import Label

import random
import numpy as np
import json

def gemerate_ipv4():
    return ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
    
class MyNetwork:
    items = []
    connections = []
    consts = {}
    # view_pos = [0,0]
    # scale = 1



class MainWidget(BoxLayout):
    item_type = ""
    link_devices = [None,None]
    def select_router(self,state):
        self.item_type = "Router" if state == "down" else ""
        for w in MyNetwork.items:
            w["widget"].canvas.before.clear()
    
    def select_end_device(self,state):
        self.item_type = "End Device" if state == "down" else ""
        for w in MyNetwork.items:
            w["widget"].canvas.before.clear()

    def clear_network(self):
        network_widget = self.ids.network_widget
        network_widget.clear_widgets()
        MyNetwork.items = []
        MyNetwork.connections = []
        for w in MyNetwork.items:
            w["widget"].canvas.before.clear()
        network_widget.canvas.before.clear()
        print("Clear Network")      
    
    def on_network_widget_touch(self,*args,**kwargs):
        network_widget = self.ids.network_widget
        touch_x, touch_y = args[1].pos 
        
        if touch_x < 0 or touch_x > network_widget.width or touch_y < 0 or touch_y > network_widget.height:
            return
        if args[1].button == "left":
            self.handle_left_click( pos=(touch_x, touch_y))
        elif args[1].button == "right":
            self.ids.router_button.state = "normal"
            self.ids.device_button.state = "normal"
            self.item_type = ""

    def select_link(self,state):
        if state == "down":
            self.item_type = "Link"
        else:
            self.link_devices = [None,None]
            self.item_type = ""
            for w in MyNetwork.items:
                w["widget"].canvas.before.clear()

    def on_widget_press_callback(self,instance,*args):
        network_widget = self.ids.network_widget
        pos = args[0].pos
        min_d = dp(100000)
        min_i = -1

        for index in range(len(MyNetwork.items)):
            item_zip = MyNetwork.items[index]
            widget = item_zip["widget"]
            device = item_zip["item"]

            # add a circle on widget.x and widget.y
            d = (widget.x + widget.size[0]/2 - pos[0])**2 + (widget.y + widget.size[1]/2 - pos[1])**2
            if item_zip['type'] == "router":
                d = (widget.x + widget.size[0]/2 - pos[0])**2 + (widget.y + widget.size[1]/2 - dp(40)+ dp(20*len(device.interfaces)) - pos[1])**2
            if d < min_d:
                min_d = d
                min_i = index
        if min_i == -1: return
        if min_d > dp(200): return
        selected_item = MyNetwork.items[min_i]

        print(min_d)
        # if the right click is pressed remove the widget
        if args[0].button == "right":
            # del widget with right click
            if self.item_type != "Link":
                if selected_item["type"] == "router":
                    wrapper = MyNetwork.items[min_i]["widget"]
                    network_widget.remove_widget(wrapper)
                    MyNetwork.items.pop(min_i)
                    # delete all connections related to this router
                    for i in range(len(MyNetwork.connections)-1,-1,-1):
                        if MyNetwork.connections[i]["device1"]['item'].ipv4 == selected_item['item'].ipv4 or MyNetwork.connections[i]["device2"]['item'].ipv4 == selected_item['item'].ipv4:
                            MyNetwork.connections.pop(i)

                elif selected_item["type"] == "end_device":
                    wrapper = MyNetwork.items[min_i]["widget"]
                    network_widget.remove_widget(wrapper)
                    MyNetwork.items.pop(min_i)
        elif args[0].button == "left":
            # if the item type is link handle
            if self.item_type == "Link":
                if selected_item["type"] == "router":
                    if self.link_devices[0] == None or self.link_devices[0] == selected_item:
                        self.link_devices[0] = selected_item
                        print("added first device")
                        # make the image of the widget instance red

                        selected_item["widget"].canvas.before.clear()
                        with selected_item["widget"].canvas.before:
                            Color(1, 0, 0, 1)
                            Rectangle(pos=(selected_item["widget"].pos[0]+dp(60),selected_item["widget"].pos[1]+dp(20) + dp(20*len(self.link_devices[0]['item'].interfaces))), size=(dp(40), dp(40)))
                        return
                    elif self.link_devices[1] == None:
                        self.link_devices[1] = selected_item
                        print("added second device")
                        # clear the backgrounds of the device 1 and 2
                        self.link_devices[0]["widget"].canvas.before.clear()
                        self.link_devices[1]["widget"].canvas.before.clear()

                        # there shouldnt be a link between the two devices already
                        for conn in MyNetwork.connections:
                            if (conn["device1"]['item'].ipv4 == self.link_devices[0]['item'].ipv4 and conn["device2"]['item'].ipv4 == self.link_devices[1]['item'].ipv4) or (conn["device1"]['item'].ipv4 == self.link_devices[1]['item'].ipv4 and conn["device2"]['item'].ipv4 == self.link_devices[0]['item'].ipv4):
                                print("Link already exists")
                                self.link_devices = [None,None]
                                return

                        # link the devices here
                        print("linking devices...",end=" ")
                        
                        device1 = self.link_devices[0]["item"]
                        device2 = self.link_devices[1]["item"]

                        cost = self.ids.link_cost.text
                        # regex test
                        try:
                            cost = float(cost)
                        except:
                            print("Invalid Cost")
                            self.link_devices = [None,None]
                            return

                        # propagation_speed = random.randint(100000000, 1000000000)
                        propagation_speed = 10e6 * cost


                        link = device1.link(device2,propagation_speed=propagation_speed)
                        if link != None:
                            print("ok!")
                            # here add a strait line between the two devices
                            with network_widget.canvas.before:
                                Color(0, 0, 0, 1)
                                new_x_1 = self.link_devices[0]["widget"].pos[0] + dp(80)
                                new_y_1 = self.link_devices[0]["widget"].pos[1] + dp(40) + dp(20*len(self.link_devices[0]['item'].interfaces))
                                new_x_2 = self.link_devices[1]["widget"].pos[0] + dp(80)
                                new_y_2 = self.link_devices[1]["widget"].pos[1] + dp(40) + dp(20*len(self.link_devices[1]['item'].interfaces))
                                Line(points=[new_x_1,new_y_1,new_x_2,new_y_2], width=dp(2))
                                # add on the middle of the line text
                                Label(text=f"{cost:.2f}",pos=(
                                    new_x_1 + (new_x_2 - new_x_1)/2 - dp(80),
                                    new_y_1 + (new_y_2 - new_y_1)/2 + dp(10)
                                ),font_size=dp(10),color=(0,0,0,1),halign='center',valign='middle',size_hint=(None, None),size=(dp(160), dp(20)))


                            # add the link to the network
                            MyNetwork.connections.append({
                                "device1":self.link_devices[0],
                                "device2":self.link_devices[1],
                                "link":link,
                                "cost":cost
                                })
                        else:
                            print("failed! Probably not enaph available ports" )
                        self.link_devices = [None,None]
                        return
                elif selected_item["type"] == "end_device":
                    print("End Device Selected for linking")
            else:
                if selected_item["type"] == "router":
                    print("Router Selected")
                elif selected_item["type"] == "end_device":
                    print("End Device Selected")

    def handle_left_click(self, pos):
        network_widget = self.ids.network_widget
        image = None
        size = dp(40)

        if self.item_type == "Router":
            # generate router
            router_ipv4 = gemerate_ipv4()
            interfaces = [gemerate_ipv4() for _ in range(random.randint(1, 4))]
            router = Router(router_ipv4, interfaces)

            # create widget
            wrapper = BoxLayout(
                orientation='vertical',
                size_hint=(None, None),
                size=(dp(160), dp(160)),
                pos=(pos[0] - dp(160) / 2, pos[1] - dp(160) / 2 + dp(20) - dp(5*len(interfaces))),
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

        self.ids.network_widget.canvas.before.clear()
        for connection in MyNetwork.connections:
            # {"points":[self.link_devices[0]["widget"].pos[0]+dp(80),self.link_devices[0]["widget"].pos[1]+dp(80),self.link_devices[1]["widget"].pos[0]+dp(80),self.link_devices[1]["widget"].pos[1]+dp(80)], "width":dp(2)}
            with self.ids.network_widget.canvas.before:
                Color(0, 0, 0, 1)
                new_x_1 = connection['device1']["widget"].pos[0] + dp(80)
                new_y_1 = connection['device1']["widget"].pos[1] + dp(40) + dp(20*len(connection['device1']['item'].interfaces))
                new_x_2 = connection['device2']["widget"].pos[0] + dp(80)
                new_y_2 = connection['device2']["widget"].pos[1] + dp(40) + dp(20*len(connection['device2']['item'].interfaces))
                
                Line(points=[new_x_1,new_y_1,new_x_2,new_y_2], width=dp(2))
                cost = connection["cost"]
                Label(text=f"{cost:.2f}",pos=(
                                    new_x_1 + (new_x_2 - new_x_1)/2 - dp(80),
                                    new_y_1 + (new_y_2 - new_y_1)/2 + dp(10)
                                ),font_size=dp(10),color=(0,0,0,1),halign='center',valign='middle',size_hint=(None, None),size=(dp(160), dp(20)))
        
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
        
        for w in MyNetwork.items:
            w["widget"].canvas.before.clear()
    
        mouse_event = args[1]
        center = mouse_event.opos
        
        self.ids.network_widget.canvas.before.clear()
        for connection in MyNetwork.connections:
            # {"points":[self.link_devices[0]["widget"].pos[0]+dp(80),self.link_devices[0]["widget"].pos[1]+dp(80),self.link_devices[1]["widget"].pos[0]+dp(80),self.link_devices[1]["widget"].pos[1]+dp(80)], "width":dp(2)}
            with self.ids.network_widget.canvas.before:
                Color(0, 0, 0, 1)
                new_x_1 = (connection['device1']["widget"].pos[0] - center[0])*1.2 + center[0] + dp(80)
                new_y_1 = (connection['device1']["widget"].pos[1] - center[1])*1.2 + center[1] + dp(40) + dp(20*len(connection['device1']['item'].interfaces))
                new_x_2 = (connection['device2']["widget"].pos[0] - center[0])*1.2 + center[0] + dp(80)
                new_y_2 = (connection['device2']["widget"].pos[1] - center[1])*1.2 + center[1] + dp(40) + dp(20*len(connection['device2']['item'].interfaces))
                
                Line(points=[new_x_1,new_y_1,new_x_2,new_y_2], width=dp(2))
                cost = connection["cost"]
                Label(text=f"{cost:.2f}",pos=(
                                    new_x_1 + (new_x_2 - new_x_1)/2 - dp(80),
                                    new_y_1 + (new_y_2 - new_y_1)/2 + dp(10)
                                ),font_size=dp(10),color=(0,0,0,1),halign='center',valign='middle',size_hint=(None, None),size=(dp(160), dp(20)))
        

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

        
        self.ids.network_widget.canvas.before.clear()
        for connection in MyNetwork.connections:
            # {"points":[self.link_devices[0]["widget"].pos[0]+dp(80),self.link_devices[0]["widget"].pos[1]+dp(80),self.link_devices[1]["widget"].pos[0]+dp(80),self.link_devices[1]["widget"].pos[1]+dp(80)], "width":dp(2)}
            with self.ids.network_widget.canvas.before:
                Color(0, 0, 0, 1)
                new_x_1 = (connection['device1']["widget"].pos[0] - center[0])/1.2 + center[0] + dp(80)
                new_y_1 = (connection['device1']["widget"].pos[1] - center[1])/1.2 + center[1] + dp(40) + dp(20*len(connection['device1']['item'].interfaces))
                new_x_2 = (connection['device2']["widget"].pos[0] - center[0])/1.2 + center[0] + dp(80)
                new_y_2 = (connection['device2']["widget"].pos[1] - center[1])/1.2 + center[1] + dp(40) + dp(20*len(connection['device2']['item'].interfaces))
                
                Line(points=[new_x_1,new_y_1,new_x_2,new_y_2], width=dp(2))
                cost = connection["cost"]
                Label(text=f"{cost:.2f}",pos=(
                                    new_x_1 + (new_x_2 - new_x_1)/2 - dp(80),
                                    new_y_1 + (new_y_2 - new_y_1)/2 + dp(10)
                                ),font_size=dp(10),color=(0,0,0,1),halign='center',valign='middle',size_hint=(None, None),size=(dp(160), dp(20)))
        

        for index in range(len(MyNetwork.items)):
            item_zip = MyNetwork.items[index]
            widget = item_zip["widget"]
            widget.x = (item_zip["pos"][0] - center[0])/1.2 + center[0]
            widget.y = (item_zip["pos"][1] - center[1])/1.2 + center[1]

            MyNetwork.items[index]["pos"] = (widget.x,widget.y)

    def generate_consts(self):
        number_of_routers = 0
        for i in MyNetwork.items:
            if i["type"] == "router":
                number_of_routers += 1
        
        costs = {}
        for i in MyNetwork.connections:
            device1 = i["device1"]["item"]
            device2 = i["device2"]["item"]
            link = i["link"]
            
            cost = link.propagation_speed/10e6 # TODO make it better baced on the disttance
            cost += device1.getTraficCost()
            cost += device2.getTraficCost()

            if device1.ipv4 not in costs.keys():
                costs[device1.ipv4] = {}
            if device2.ipv4 not in costs.keys():
                costs[device2.ipv4] = {}

            costs[device1.ipv4][device2.ipv4] = cost
            costs[device2.ipv4][device1.ipv4] = cost
        MyNetwork.consts = costs

        set_of_ruters = set()
        for key, value in costs.items():
            set_of_ruters.add(key)
            for key2, value2 in value.items():
                set_of_ruters.add(key2)
        keys = list(set_of_ruters)
        
        return costs , keys

    def run_network(self):
        costs, keys = self.generate_consts()
        
        start_ip = self.ids.start_ip.text
        end_ip = self.ids.end_ip.text

        if start_ip not in keys or end_ip not in keys:
            print("Invalid IPs")
            return
        
        res = solve(costs, start_ip, end_ip)
        print("Run Network: ",res)

        # color the connections of active links
        path = res['path']
        for conn in MyNetwork.connections:
            ip_1 = conn["device1"]["item"].ipv4
            ip_2 = conn["device2"]["item"].ipv4

            for p in path:
                ip_1_p = p['src']
                ip_2_p = p['dest']

                if (ip_1 == ip_1_p and ip_2 == ip_2_p) or (ip_1 == ip_2_p and ip_2 == ip_1_p):
                    # color the connection
                    with self.ids.network_widget.canvas.before:
                        Color(0, 0.5, 1, 1)
                        new_x_1 = (conn['device1']["widget"].pos[0])+ dp(80)
                        new_y_1 = (conn['device1']["widget"].pos[1]) + dp(40) + dp(20*len(conn['device1']['item'].interfaces))
                        new_x_2 = (conn['device2']["widget"].pos[0])+ dp(80)
                        new_y_2 = (conn['device2']["widget"].pos[1]) + dp(40) + dp(20*len(conn['device2']['item'].interfaces))
                        
                        Line(points=[new_x_1,new_y_1,new_x_2,new_y_2], width=dp(2))
                

    def export_network(self):
        costs = self.generate_consts()

        print("Export Network")
        
        # write the costs to export json file
        with open('export.json', 'w') as fp:
            json.dump(costs, fp)

    def loadPackets(self,ip):
        # load the packets into router with ip
        router = None
        for item_zip in MyNetwork.items:
            if item_zip["type"] == "router" and item_zip["item"].ipv4 == ip:
                router = item_zip["item"]
                break
        
        if router == None:
            print("Invalid IP")
            return
        
        # packets
        packets = [Packet('test_ip1', 'test_ip2', "Hello World from 1") for _ in range(5)]

        # load the packets into the router
        for packet in packets:
            # put the packets for now on the first interface
            for key in router.interfaces.keys():
                router.interfaces[key].transmit_queue.put(packet)
                break

