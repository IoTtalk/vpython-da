import random

import dan
import dai
import wx

from visual import *

class Speed(dai.ODF):
    def pull(self, data):
        ida['speed'] = data[0]

class Angle(dai.ODF):
    def pull(self, data):
        ida['angle'] = data[0] * 3.14 * 2 / 360

class IDA:
    def __setitem__(self, key, value):
        self.values[key] = value
        self.dirty[key] = True

    def __getitem__(self, key):
        if self.dirty.get(key):
            self.dirty[key] = False
            return self.values[key]

        return self.defaults[key]

    def __init__(self):
        self.suspended = True
        self.defaults = {
            'speed': 0,
            'angle': 45 * 3.14 / 180,
        }
        self.values = {}
        self.dirty = {}
        self.g = 9.8
        self.dt = 0.001

    def iot_app(self):
        class window_n(window):
            def __init__(self, **kwargs):
                super(window_n, self).__init__(**kwargs)
                self.win.Bind(wx.EVT_CLOSE, self.exit)

            def exit(self, evt):
                dan.deregister()
                super(window_n, self)._OnExitApp(evt)

        my_window = window_n(title='Sliding' + mac_addr, width=1000, height=650)
        scene = display(window=my_window, width=1000, height=800,
                forward=vector(-1, -1, -3),
                background=vector(0.6, 0.3, 0.2),
                center=vector(2.5, 1, 0),
                range=4
        )
        init_value_box = label(
                pos=vector(4.0, 2.5, 0),
                height=25,
                border=15,
                font='monospace',
                color=color.white,
                text='Initial values:\n' + 'Speed:\n' + 'Angle:',
        )
        spd_box = label(
                pos=vector(4.0, 1.5, 0),
                height=25,
                border=15,
                font='monospace',
                color=color.white,
                text='Speed in animation:\n',
        )

        while True:
            if self.suspended:
                sleep(1)
                continue

            speed = self['speed']
            angle = self['angle']

            if angle < 0.523:
                angle = 0.523
            if angle > 1.047:
                angle = 1.047


            init_value_box.text = 'Initial values:\nFriction: 0.5\nSpeed: {:.1f}'.format(round(speed, 1))
            frame_count = 0
            under_board = Polygon(
                [(-0.1*sin(angle), - 0.1 * cos(angle) + 2),
                 (2-0.1*sin(angle), 2 - 2/tan(angle) - 0.1 * cos(angle))
                ]
            )
            straight = [(0, 0, 0.75), (0, 0, -0.75)]
            floor = extrusion(
                pos=straight,
                shape=under_board,
                color=color.green
            )
            ball = sphere(
                pos=vector(0, 2, 0),
                radius=0.1,
                color=color.white
            )
            ball.velocity = vector(speed * sin(angle), -speed * cos(angle), 0.0)
            init_value_box.text = 'Initial values:\nSpeed: <{:+03.1f}, {:+03.1f}, {:+03.1f}>\nAngle: {:f}'.format(
                round(ball.velocity.x, 2),
                round(ball.velocity.y, 2),
                round(ball.velocity.z, 2),
                round(angle * 360 / 3.14 / 2, 2),
            )
            a = vector(self.g * cos(angle) * sin(angle), - self.g * cos(angle) * cos(angle), 0)

            while True:
                rate(1000)
                ball.pos = ball.pos + ball.velocity * self.dt + 0.5 * a * self.dt ** 2
                ball.velocity = ball.velocity + a * self.dt
                if frame_count % 10 == 0:
                    spd_box.text = 'Speed:\n <{:+03.1f}, {:+03.1f}, {:+03.1f}>'.format(
                        round(ball.velocity.x, 2), round(ball.velocity.y, 2), round(ball.velocity.z, 2)
                    )
                frame_count += 1
                if ball.x >= 2 - 0.1 * sin(angle):
                    break
            sleep(1)
            ball.visible = False
            floor.visible = False


ida = IDA()
endpoint = 'http://localhost:9999'
mac_addr = '00' + ''.join(hex(random.randint(0, 16))[2:] for i in range(10))
profile = {
    'd_name': 'sample da - sliding',
    'dm_name': 'Ball-Slid',
    'u_name': 'yb',
    'is_sim': False,
}

dai.main(globals())