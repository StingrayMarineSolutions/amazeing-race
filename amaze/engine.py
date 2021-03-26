import numpy as np
import cv2


class Sprite(object):
    def __init__(self, filenames, offset):
        self.current_frame = 0
        self.width = None
        self.height = None
        self.frames = self.load_frames(filenames)
        self.offset_x, self.offset_y = offset

    def load_frames(self, filenames):
        frames = []
        for filename in filenames:
            im = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
            rgb = im[..., :3]
            alpha = im[..., 3].astype(np.bool)
            frames.append( (rgb, alpha) )
            self.height, self.width, _ = im.shape
        return frames

    def draw(self, img, pos):
        rgb, alpha = self.frames[self.current_frame]

        x, y = tuple(pos)
        x, y = x - self.offset_x, y - self.offset_y

        y1, y2 = max(0, y), min(img.shape[0], y + rgb.shape[0])
        x1, x2 = max(0, x), min(img.shape[1], x + rgb.shape[1])

        y1o, y2o = max(0, -y), min(rgb.shape[0], img.shape[0] - y)
        x1o, x2o = max(0, -x), min(rgb.shape[1], img.shape[1] - x)

        img_crop = img[y1:y2, x1:x2]
        rgb_crop = rgb[y1o:y2o, x1o:x2o]
        alpha_crop = alpha[y1o:y2o, x1o:x2o]
        img_crop[alpha_crop] = rgb_crop[alpha_crop]

        self.current_frame = (self.current_frame + 1) % len(self.frames)

        return img


class Engine():
    PLAYER_RADIUS = 6

    def __init__(self, scene, visualize=True, consume_input=False, render=True, max_speed=10):
        self.scene = scene
        self.max_speed = max_speed
        self.visualize = visualize
        self.consume_input = consume_input
        self.initialized = False
        self.img = None
        self.mask = None
        self.pos = None
        self.goal = None
        self.render_scene = render
        self.louse_sprite = Sprite([f'resource/image/louse_{i}.png' for i in range(8)], offset=(85, 15))
        self.win_sprite = Sprite([f'resource/image/burning_{i}.png' for i in range(8)], offset=(84, 67))
        self.player_sprite = Sprite(['resource/image/laser-dot.bmp'], offset=(6, 6))
        self.loss_sprite = Sprite(['resource/image/laser-dot-wrong.png'], offset=(6, 6))
        self.img_cache = None

    def forward(self, action):
        '''
        Runs an iteration of the gameloop

        :param action: action to perform. Pass None to initialize first frame
        :return: (scene, pos, status) Image of scene pluss vector of position (np.array([x, y]))
        '''
        if action is None:
            assert not self.initialized, "Can't initialize game twice"
            self.initialized = True
            self.img, self.mask, self.pos, self.goal = self.scene.generate()
            if self.visualize:
                cv2.namedWindow('GAME', cv2.WINDOW_NORMAL)
        else:
            self.img, self.mask = self.scene.update()
            assert self.img.dtype == np.uint8, 'Maze img must have dtype np.uint8'
            assert self.mask.dtype == np.uint8, 'Maze mas must have dtype np.uint8'
            action = self.validate_action(action, self.pos, self.mask)
            if self.check_collision(action, self.pos, self.mask):
                self.pos = self.update_position(self.pos, action)
                return None, None, 'GAME OVER'
            self.pos = self.update_position(self.pos, action)
            if self.check_finished(self.pos, self.goal):
                return None, None, 'YOU WON'
        view = None
        if self.render_scene or self.visualize:
            view = self.render(self.img, self.pos, self.goal)
        if self.visualize:
            self.show_scene(view)
        return view, self.pos.copy(), 'RUNNING'

    def update_position(self, pos, action):
        return pos + action

    def check_collision(self, action, pos, mask):
        next_pos = pos + action
        if np.any(next_pos < self.PLAYER_RADIUS) or np.any(next_pos+self.PLAYER_RADIUS >= mask.shape):
            return True
        roi = (min(pos[0], next_pos[0])-self.PLAYER_RADIUS, min(pos[1], next_pos[1])-self.PLAYER_RADIUS), \
              (max(pos[0], next_pos[0])+1+self.PLAYER_RADIUS, max(pos[1], next_pos[1])+1+self.PLAYER_RADIUS)
        mask = mask[roi[0][1]:roi[1][1], roi[0][0]:roi[1][0]]
        line = np.zeros_like(mask)
        cv2.line(line, (0, 0), mask.shape, 255, self.PLAYER_RADIUS * 2)
        sampled_points = mask[line > 0]
        return np.any(sampled_points > 0)

    def check_finished(self, pos, goal):
        return np.linalg.norm(pos-goal) < 10

    def validate_action(self, action, pos, mask):
        assert isinstance(action, np.ndarray), 'Action must be a numpy array'
        assert action.size == 2, 'Action must have exactly to elements'
        assert np.all(np.abs(action) <= 5), 'Action must be withing +- 5 in both dimensions'
        return action
        # return False

    def show_scene(self, img):
        cv2.imshow('GAME', img)
        if self.consume_input:
            cv2.waitKey(1)

    def animate_win(self):
        for _ in range(150):
            img, mask = self.scene.update()
            img = img.copy()
            img = self.draw_win(img, self.goal)
            self.show_scene(img)
            cv2.waitKey(20)

    def draw_win(self, img, pos):
        return self.win_sprite.draw(img, pos)

    def animate_loss(self):
        for _ in range(150):
            img, mask = self.scene.update()
            img = img.copy()
            img = self.draw_loss(img, self.pos, self.goal)
            self.show_scene(img)
            cv2.waitKey(20)

    def draw_loss(self, img, pos, goal):
        img = self.draw_target(img, goal)
        img = self.loss_sprite.draw(img, pos)
        return img

    def render(self, img, pos, goal):
        if self.img_cache is None:
            self.img_cache = img.copy()
        else:
            self.img_cache[:] = img

        img = self.img_cache
        img = self.draw_target(img, goal)
        img = self.draw_player(img, pos)
        return img

    def draw_player(self, img, pos):
        return self.player_sprite.draw(img, pos)

    def draw_target(self, img, goal):
        return self.louse_sprite.draw(img, goal)


class Game(object):
    def __init__(self, engine, player):
        self.engine = engine
        self.player = player

    def run(self):
        img, pos, status = self.engine.forward(None)
        while status == 'RUNNING':
            action = self.player.forward(img, pos)
            img, pos, status = self.engine.forward(action)
        if status == 'YOU WON':
            self.engine.animate_win()
        elif status == 'GAME OVER':
            self.engine.animate_loss()

        print('Finished with status:', status)
