import random

import wx
import dan
import dai

from visual import *

import axis_projectile


class Angle(dai.ODF):
    def pull(self, data):
        # angle that larger than 90 degrees
        #  (i.e. shoot the ball to the ground)
        #  is not permitted
        if data[0] > 90:
            data[0] = 90

        # translate degrees to radius
        ida['angle'] = data[0] * 2 * pi / 360


class Height(dai.ODF):
    def pull(self, data):
        ida['height'] = data[0]


class Speed(dai.ODF):
    def pull(self, data):
        ida['speed'] = data[0]


class IDA(object):
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
            'angle': 45 * 2 * pi / 360,
            'height': 75,
            'speed': 10,
        }
        self.values = {}
        self.dirty = {}
        self.speed_threshold = 5

    def iot_app(self):
        class window_n(window):
            def __init__(self, **kwargs):
                super(window_n, self).__init__(**kwargs)
                self.win.Bind(wx.EVT_CLOSE, self.exit)

            def exit(self, evt):
                dan.deregister()
                super(window_n, self)._OnExitApp(evt)

        my_window = window_n(title='Projectile'+ mac_addr, width=1000, height=650)
        scene = display(window=my_window, width=1000, height=1000,
                forward=vector(0.5, -0.05, -1),
                background=vector(0.6, 0.3, 0.2),
                center=vector(250, 100, 0),
                range=350
        )
        scene.bind('keydown', axis_projectile.keyInput)
        floor = box(length=500,
                height=0.5, width=250,
                pos=vector(250, 0, 0), color=vector(0, 1, 0)
        )
        init_value_box = label(
                pos=vector(200, 251, 0),
                height=25,
                border=15,
                font='monospace',
                color=color.white,
                text='\n'.join([
                    'Initial values:',
                    'Height: ',
                    'Angle: ',
                    'Speed: ',
                ])
        )
        ball_pos_box = label(
                pos=vector(400, 270, 0),
                height=25,
                border=15,
                font='monospace',
                color=color.white,
                text='\n'.join([
                    'Position:',
                    'X: ',
                    'Y: ',
                    'Z: ',
                ])
        )

        ball = sphere(
            radius=8,
            color=color.white
        )
        g = 9.8
        dt = 0.005
        while True:
            if self.suspended:
                sleep(1)
                continue

            angle = self['angle']
            height = self['height']
            speed = self['speed']

            if speed < self.speed_threshold:
                continue

            ball_touch = 0
            frame_count = 0
            ball.visible = True
            ball.pos = vector(0, height + 8.25, 0)

            ball.velocity = vector(
                    speed * cos(angle),
                    speed * sin(angle),
                    0
            )
            init_value_box.text = '\n'.join([
                    'Initial values:',
                    'Height: {:.1f}'.format(height),
                    'Angle: {}'.format(angle * 360 / 2 / pi),
                    'Speed: {:.1f}'.format(speed),
            ])

            while True:
                rate(1000)
                a = vector(0, -g, 0)
                ball.pos = ball.pos + ball.velocity * dt + 0.5 * a * (dt ** 2)
                if ball.y < 8.25 and ball.velocity.y < 0:
                    ball.velocity.y = - ball.velocity.y
                    ball_touch += 1
                else:
                    ball.velocity = ball.velocity + a * dt

                if ball.x > 500 or ball_touch == 10:
                    break

                if frame_count % 1000 == 0 or True:
                    ball_pos_box.text = '\n'.join([
                        'Position:',
                        'X: {:.1f}'.format(ball.x),
                        'Y: {:.1f}'.format(ball.y),
                        'Z: {:.1f}'.format(ball.z),
                    ])

                frame_count += 1

            ball.visible = False


ida = IDA()
endpoint = 'http://localhost:9999'
mac_addr = '00' + ''.join(hex(random.randint(0, 16))[2:] for i in range(10))
profile = {
    'd_name': 'sample da',
    'dm_name': 'Ball-Projectile',
    'u_name': 'yb',
    'is_sim': False,
}

dai.main(globals())
