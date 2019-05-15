from controller import Controller



class TestController(object):

    def setup(self):
        self.controller = Controller()

    def teardown(self):
        pass

    def test_init(self):
        assert self.controller.offset == [0, 0]
        assert self.controller.scale == [1.0, 1.0]

        assert isinstance(self.controller.current_name, str)

