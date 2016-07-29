import random

import wx
import dan
import dai

from visual import *

import axis_projectile


class Angle(dai.ODF):
    def __init__(self):
        super(Angle, self).__init__('Angle')

    def pull(self, data):
        # angle that larger than 90 degrees
        #  (i.e. shoot the ball to the ground)
        #  is not permitted
        if data[0] > 90:
            data[0] = 90

        # translate degrees to radius
        ida.values['angle'] = data[0] * 2 * pi / 360
        ida.dirty['angle'] = True


class Height(dai.ODF):
    def __init__(self):
        super(Height, self).__init__('Height')

    def pull(self, data):
        ida.values['height'] = data[0]
        ida.dirty['height'] = True


class Speed(dai.ODF):
    def __init__(self):
        super(Speed, self).__init__('Speed')

    def pull(self, data):
        ida.values['speed'] = data[0]
        ida.dirty['speed'] = True


def init_df_list():
    add_df(
        Angle(),
        Height(),
        Speed(),
    )


def init_cmd_list():
    pass


class IDA:
    def __init__(self):
        self.suspended = True
        self.dirty = {
            'angle': False,
            'height': False,
            'speed': False,
        }
        self.defaults = {
            'angle': 45 * 2 * pi / 360,
            'height': 75,
            'speed': 10,
        }
        self.values = {key: self.defaults[key] for key in self.defaults}
        self.speed_threshold = 5

    @property
    def angle(self):
        return self.values['angle']

    @property
    def height(self):
        return self.values['height']

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
                color=color.white
        )
        ball_pos_box = label(
                pos=vector(400, 270, 0),
                height=25,
                border=15,
                font='monospace',
                color=color.white
        )

        ball = sphere(
            radius=8,
            color=color.white
        )
        g = 9.8
        dt = 0.005
        while True:
            for key in ['angle', 'height', 'speed']:
                if not self.dirty[key]:
                    self.values[key] = self.defaults[key]

                self.dirty[key] = False

            if self.values['speed'] < self.speed_threshold:
                continue

            ball_touch = 0
            frame_count = 0
            ball.visible = True
            ball.pos = vector(0, self.height + 8.25, 0)

            ball.velocity = vector(
                    self.speed * cos(self.angle),
                    self.speed * sin(self.angle),
                    0
            )
            init_value_box.text = '\n'.join([
                    'Initial values:',
                    'Height: {:.1f}'.format(self.height),
                    'Angle: {}'.format(self.angle * 360 / 2 / pi),
                    'Speed: {:.1f}'.format(self.speed),
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
            # sleep(1)

mac_addr = '00' + ''.join(hex(random.randint(0, 16))[2:] for i in range(10))
ida = IDA()

dai.main(
    'http://localhost:9999',
    mac_addr,
    {
        'd_name': 'sample da',
        'dm_name': 'Ball-Projectile',
        'u_name': 'yb',
        'is_sim': False,
    },
    ida,
    [Angle(), Height(), Speed()],
    [],
)