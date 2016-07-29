import random

import dan
import dai
import wx

from visual import *

class Speed(dai.ODF):
    def __init__(self):
        super(Speed, self).__init__('Speed')

    def pull(self, data):
        ida.values['speed'] = data[0]
        ida.dirty['speed'] = True

class IDA:
    def __init__(self):
        self.suspended = True
        self.dirty = {
            'speed': False,
        }
        self.defaults = {
            'speed': 10,
        }
        self.values = {key: self.defaults[key] for key in self.defaults}
        self.speed_threshold = 5
        self.g = 9.8
        self.m = 0.5
        self.fric_coef = 0.5
        self.dt = 0.003
        self.s = 0.01
        self.ball_inertia = 2 * self.m * 0.35 ** 2 / 3
        self.torque = -self.fric_coef * self.m * self.g * self.s
        self.a = self.torque / self.ball_inertia
        self.speed_former = self.speed

    @property
    def speed(self):
        return self.values['speed']

    def iot_app(self):
        class window_n(window):
            def __init__(self, **kwargs):
                super(window_n, self).__init__(**kwargs)
                self.win.Bind(wx.EVT_CLOSE, self.exit)

            def exit(self, evt):
                dan.deregister()
                super(window_n, self)._OnExitApp(evt)

        my_window = window_n(title='Spin'+ mac_addr, width=700, height=700)
        scene = display(window=my_window, width=700, height=700,
                forward=vector(0, -0.8, -1),
                background=vector(1, 1, 1),
                center=vector(0, 0.25, 0),
                range=1
        )
        floor = box(length=3,
                height=0.01, width=2,
                material=materials.wood,
        )
        init_value_box = label(
                pos=vector(-0.45, 0.9, 0),
                height=25,
                border=15,
                font='monospace',
                color=color.black,
                linecolor=color.black,
                text='Initial values:\nFriction: 0.5\nSpeed:',
        )
        ball_pos_box = label(
                pos=vector(0.45, 0.9, 0),
                height=25,
                border=15,
                font='monospace',
                color=color.black,
                linecolor=color.black,
                text='Speed:',
        )

        ball = sphere(
            radius=0.35,
            pos=vector(0, 0.35, 0.1),
            material=materials.earth,
        )
        
        while True:
            for key in ['speed']:
                if not self.dirty[key]:
                    self.values[key] = self.defaults[key]

                self.dirty[key] = False

            if self.speed > 10:
                self.speed = 10

            speed = self.speed

            init_value_box.text = 'Initial values:\nFriction: 0.5\nSpeed: ' + str(round(speed, 1))
            frame_count = 0

            while True:
                rate(1000)
                speed += self.a * self.dt
                delta_angle = speed * self.dt + 0.5 * self.a * self.dt **2
                ball.rotate(angle = delta_angle, axis = vector(0, 1, 0))
                if frame_count % 1000 == 0:
                    ball_pos_box.text = 'Speed:' + str(round(speed, 1))
                frame_count += 1
                if self.speed_former * speed <= 0:
                    break
                self.speed_former_former = speed
                
            # sleep(1)

mac_addr = '00' + ''.join(hex(random.randint(0, 16))[2:] for i in range(10))
ida = IDA()

dai.main(
	#'http://140.113.199.227:9999',
	'http://localhost:9999',
    mac_addr,
	{
		'd_name': 'sample da - Spin',
		'dm_name': 'Ball-Spin',
		'u_name': 'yb',
		'is_sim': False,
	},
    ida,
    [Speed()],
    [],
)