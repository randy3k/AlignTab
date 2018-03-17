import sublime
from unittest import TestCase

version = sublime.version()


class TestUFlag(TestCase):

    def setUp(self):
        self.view = sublime.active_window().new_file()
        # make sure we have a window to work with
        s = sublime.load_settings("Preferences.sublime-settings")
        s.set("close_windows_when_empty", False)

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            self.view.window().run_command("close_file")

    def setText(self, string):
        self.view.settings().set("auto_indent", False)
        self.view.run_command("insert", {"characters": string})

    def getRow(self, row):
        return self.view.substr(self.view.line(self.view.text_point(row - 1, 0)))

    def test_u_flag(self):
        string = "apple =  1==0\n  banana = 100\n   car =    2"
        self.setText(string)
        self.view.run_command("align_tab", {"user_input": "=/uclf1"})

        first_row = self.getRow(1)
        self.assertEqual(first_row, "apple    = 1==0")
