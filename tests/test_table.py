import sublime
from UnitTesting.unittesting import DeferrableTestCase

import AlignTab.hist as hist
history = hist.history

version = sublime.version()


class TestTable(DeferrableTestCase):

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
        self.view.run_command("insert", {"characters": string})

    def getRow(self, row):
        return self.view.substr(self.view.line(self.view.text_point(row - 1, 0)))

    def test_table_mode(self):
        string = """a | b |   c
        d |   e |f"""
        self.setText(string)
        self.view.run_command("align_tab", {"user_input": "\\|", "mode": True})
        history.insert("\\|")
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(1, 1))
        self.setText("pple")
        yield 400
        second_row = self.getRow(2)
        self.assertEqual(second_row, "d     | e | f")

    def test_latex_table(self):
        string = r"""  \letter{S} \\ \hline
    Some text                      & the second column & short \\ \hline
    Some more text that is aligned & the second column & longer than short \\ \hline
  \letter{T} \\ \hline
    Totally related text & that is aligned differently, unfortunately & blah \\ \hline"""
        self.setText(string)
        self.view.run_command("select_all")
        self.view.run_command("align_tab", {"user_input": "&", "mode": True})
        history.insert("&")
        self.view.sel().clear()
        yield 400
        self.view.sel().add(sublime.Region(0, 0))
        self.setText("\n")
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(157, 157))
        self.setText("abc")
        yield 400
        second_row = self.getRow(6)
        self.assertEqual(second_row,
                         r"      Totally related text              " +
                         r"& that is aligned differently, unfortunately & blah \\ \hline")

    def test_no_new_line(self):
        # https://github.com/randy3k/AlignTab/issues/78
        string = """I = a  | b  | aP | bP
S = a  |
        """
        self.setText(string)
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(30, 30))
        self.view.run_command("align_tab", {"user_input": "\\|", "mode": True})
        history.insert("\\|")
        yield 400
        self.setText(" ")
        yield 1000
        self.assertEqual(self.view.sel()[0].end(), 28)
