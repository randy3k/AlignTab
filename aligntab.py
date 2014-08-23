import sublime
import sublime_plugin
import re
from .parser import input_parser
from .hist import history
from .table import toogle_table_mode
from .aligner import Aligner

def get_named_pattern(user_input):
    s = sublime.load_settings('AlignTab.sublime-settings')
    patterns = s.get('named_patterns', {})
    if user_input in patterns:
        user_input = patterns[user_input]
    elif user_input == 'last_regex' and history.last():
        user_input = history.last()
    return user_input

class AlignTabCommand(sublime_plugin.TextCommand):
    def run(self, edit, user_input=None, mode=False, live_preview=False):
        view = self.view
        if not user_input:
            self.aligned = False
            v = self.view.window().show_input_panel('Align By RegEx:', '',
                    # On Done
                    lambda x: self.on_done(x, mode, live_preview),
                    # On Change
                    lambda x: self.on_change(x) if live_preview else None,
                    # On Cancel
                    lambda: self.on_change(None) if live_preview else None )

            v.settings().set('AlignTabInputPanel', True)


        elif user_input:
                user_input = get_named_pattern(user_input)
                [regex, flag, f] = input_parser(user_input)
                regex = '(' + regex + ')'

                # apply align_tab
                aligner = Aligner(view, regex, flag, f)
                self.aligned = aligner.run(edit, mode)

                if self.aligned:
                    if mode:
                        toogle_table_mode(view, True)
                    else:
                        sublime.status_message("")
                else:
                    if mode and not aligner.prev_next_match():
                        toogle_table_mode(view, False)
                    else:
                        sublime.status_message("[Pattern not Found]")

    def on_change(self, user_input):
        view = self.view
        # Undo the previous change if needed
        if self.aligned:
            self.view.run_command("soft_undo")
            self.aligned = False
        if user_input:
            self.view.run_command("align_tab", {"user_input":user_input, "live_preview":True})

    def on_done(self, user_input, mode, live_preview):
        view = self.view
        history.insert(user_input)
        # do not double align when done with live preview mode
        if not live_preview:
            self.view.run_command("align_tab", {"user_input":user_input, "mode":mode})
