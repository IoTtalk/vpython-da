import random

import dan
import dai
import wx

from visual import *

class Number(dai.ODF):
    def __init__(self):
        super(Number, self).__init__('Number')

    def pull(self, data):
        ida.values['number'] = data[0]
        ida.dirty['number'] = True

class IDA:
    def __init__(self):
        self.suspended = True
        self.dirty = {
            'number': False,
        }
        self.defaults = {
            'number': 5,
        }
        self.values = {key: self.defaults[key] for key in self.defaults}
        self.dt = 0.0025

    @property
    def number(self):
        return self.values['number']

    def iot_app(self):
        class window_n(window):
            def __init__(self, **kwargs):
                super(window_n, self).__init__(**kwargs)
                self.win.Bind(wx.EVT_CLOSE, self.exit)

            def exit(self, evt):
                dan.deregister()
                super(window_n, self)._OnExitApp(evt)

        my_window = window_n(title='Specular reflection' + mac_addr, width=700, height=700)
        scene = display(window=my_window, width=700, height=700,
                background=vector(0.8, 0.8, 0.8),
                center=vector(0, 0, 5),
                range=1,
                fov=0.04,
        )
        init_value_box = label(
                pos=vector(-0.7, -0.5, 0),
                height=25,
                border=15,
                font='monospace',
                color=color.black,
                linecolor=color.black,
                text='Initial values:\nNumber:',
        )
        mirror_list = [0.005 * t for t in range(-314, 314)] 
        mirror_shape = [(-1 * cos(theta), 1 * sin(theta) ) for theta in mirror_list] 
        straight = [(0, 0, -0.5), (0, 0, 0.5)]
        concave_mirror = extrusion(pos = straight, shape = mirror_shape, color = color.yellow)

        def reflection(normal_vector, in_vector): 
            projection = dot(in_vector, normal_vector) * normal_vector
            trans_vector = in_vector - projection
            return trans_vector - projection
    
        while True:
            for key in ['number']:
                if not self.dirty[key]:
                    self.values[key] = self.defaults[key]

                self.dirty[key] = False

            if self.number > 15:
                self.number = 15

            init_value_box.text = 'Initial values:\nNumber: {:d}'.format(self.number)
            ray_list = []

            for i in range(self.number):
                ray = sphere(
                    pos=vector(-1, (i + 1) * 0.05, 0),
                    color=color.blue,
                    radius=1e-06,
                    make_trail=True,
                    v=vector(3.0, 0, 0),
                )
                ray_list.append(ray)
                ray.trail_object.radius = 0.003

                while True:
                    rate(1000)
                    ray.pos = ray.pos + ray.v * self.dt
                    if abs(ray.pos) >= 1 and ray.pos.x > 0 :
                        ray.v = reflection(ray.pos / abs(ray.pos), ray.v)
                    if ray.pos.y < 0 : 
                        break
                
            sleep(1)
            for obj in ray_list:
                obj.trail_object.visible = False

mac_addr = '00' + ''.join(hex(random.randint(0, 16))[2:] for i in range(10))
ida = IDA()

dai.main(
	#'http://140.113.199.227:9999',
	'http://localhost:9999',
    mac_addr,
	{
		'd_name': 'sample da - Specular reflection',
		'dm_name': 'Ball-Reflect',
		'u_name': 'yb',
		'is_sim': False,
	},
    ida,
    [Number()],
    [],
)
