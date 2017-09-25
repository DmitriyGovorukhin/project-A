import ds4drv.__main__

from ds4drv.__main__ import *

call = None


class Controller(object):
    def __init__(self, call_back):
        global call
        call = call_back
        main()


class ExtraDS4Controller(DS4Controller):
    def __init__(self, index, options, call_back):
        super().__init__(index, options, dynamic=False)
        self.call_back = call_back

    def setup_device(self, device):
        self.logger.info("Connected to {0}", device.name)
        self.device = device
        self.device.set_led(*self.options.led)
        self.fire_event("device-setup", device)
        self.loop.add_watcher(device.report_fd, self.read_report)
        self.load_options(self.options)

    def read_report(self):
        report = self.device.read_report()

        if not report:
            if report is False:
                return

            self.cleanup_device()
            return

        result = {}

        for key in report.__slots__:
            result[key] = getattr(report, key)

        self.call_back(result)


def create_extra_controller_thread(index, controller_options):
    controller = ExtraDS4Controller(index, controller_options, call)

    thread = Thread(target=controller.run, name='DS4 - controller')
    thread.daemon = True
    thread.controller = controller
    thread.start()

    return thread


ds4drv.__main__.create_controller_thread = create_extra_controller_thread
