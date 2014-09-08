import sublime, sys
from UnitTesting.unittesting import DeferrableTestCase

import AlignTab.hist as hist
history = hist.history

version = sublime.version()

class TestTable(DeferrableTestCase):

    def setUp(self):
        self.view = sublime.active_window().new_file()

    def tearDown(self):
        if self.view:
            self.view.set_scratch(True)
            # don't close the last tab in osx platform
            if len(self.view.window().views()) == 1 and sublime.platform() == "osx": return
            self.view.window().run_command("close_file")

    def setText(self, string):
        self.view.run_command("insert", {"characters": string})

    def getRow(self, row):
        return self.view.substr(self.view.line(self.view.text_point(row,0)))

    def test_table_mode(self):
        string = """a | b |   c
        d |   e |f"""
        self.setText(string)
        self.view.run_command("align_tab", {"user_input" :"\\|", "mode" : True})
        history.insert("\\|")
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(1,1))
        self.setText("pple")
        yield 400
        second_row = self.getRow(1)
        self.assertEqual(second_row,"d     | e | f")
