from controller import Controller



class TestController(object):

    def setup(self):
        self.controller = Controller()

    def teardown(self):
        pass

    def test_init(self):
        assert self.controller.offset == [0, 0]
        assert self.controller.scale == [1.0, 1.0]
        assert len(self.controller.contour.shape) == 2

        assert isinstance(self.controller.current_name, str)

        assert self.controller.background.shape == (480, 640)

    def test_calibrate(self):
        self.controller.background = None
        self.controller.calibrate()

        assert self.controller.background.shape == (480, 640)

    def test_capture(self):
        frame, depth_rgb = self.controller.capture()

        assert frame.shape == (480, 640, 3)
        assert depth_rgb.shape == (480, 640, 3)

    def get_user_details(self):
        frame, depth_rgb = self.controller.capture()

        assert frame.shape == (480, 640, 3)
        assert depth_rgb.shape == (480, 640, 3)