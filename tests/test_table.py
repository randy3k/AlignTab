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
        return self.view.substr(self.view.line(self.view.text_point(row-1,0)))

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
        second_row = self.getRow(2)
        self.assertEqual(second_row,"d     | e | f")

    def test_latex_table(self):
        string = r"""  \letter{S} \\ \hline
    Some text                      & the second column & short \\ \hline
    Some more text that is aligned & the second column & longer than short \\ \hline
  \letter{T} \\ \hline
    Totally related text & that is aligned differently, unfortunately & blah \\ \hline"""
        self.setText(string)
        self.view.run_command("select_all")
        self.view.run_command("align_tab", {"user_input" :"&", "mode" : True})
        history.insert("&")
        self.view.sel().clear()
        yield 400
        self.view.sel().add(sublime.Region(0,0))
        self.setText("\n")
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(157,157))
        self.setText("abc")
        yield 400
        second_row = self.getRow(6)
        self.assertEqual(second_row,r"      Totally related text              & that is aligned differently, unfortunately & blah \\ \hline")
