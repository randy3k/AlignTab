import sublime
import sublime_plugin
from .hist import history
from .table import toogle_table_mode
from .aligner import Aligner


def resolve_input(user_input):
    if isinstance(user_input, str):
        s = sublime.load_settings('AlignTab.sublime-settings')
        patterns = s.get('named_patterns', {})
        if user_input == 'last_regex' and history.last():
            user_input = history.last()
        if user_input in patterns:
            user_input = patterns[user_input]
    if isinstance(user_input, str):
        user_input = [user_input]
    return user_input


class AlignTabCommand(sublime_plugin.TextCommand):
    def run(self, edit, user_input=None, mode=False, live_preview=False):
        view = self.view
        if not user_input:
            self.aligned = False
            history.reset_index()
            history.roll(backwards=True)
            last = history.get()
            v = self.view.window().show_input_panel(
                'Align By RegEx:', last or "",
                # On Done
                lambda x: self.on_done(x, mode, live_preview),
                # On Change
                lambda x: self.on_change(x) if live_preview else None,
                # On Cancel
                lambda: self.on_change(None) if live_preview else None
            )
            v.run_command("select_all")
            v.settings().set('AlignTabInputPanel', True)
        else:
            user_input = resolve_input(user_input)
            error = []
            for uinput in user_input:
                # apply align_tab
                aligner = Aligner(view, uinput, mode)
                self.aligned = aligner.run(edit)

                if self.aligned:
                    if mode:
                        # to allow keybinds/commands for tablemode
                        history.insert(uinput)
                        toogle_table_mode(view, True)
                    else:
                        sublime.status_message("")
                else:
                    if mode and not aligner.adjacent_lines_match():
                        toogle_table_mode(view, False)
                    else:
                        error.append(uinput)
            if error:
                errors = '    '.join(error)
                sublime.status_message("[Patterns not Found:   " + errors + "   ]")

    def on_change(self, user_input):
        # Undo the previous change if needed
        if self.aligned:
            self.view.run_command("soft_undo")
            self.aligned = False
        if user_input:
            self.view.run_command("align_tab", {"user_input": user_input, "live_preview": True})

    def on_done(self, user_input, mode, live_preview):
        history.insert(user_input)
        # do not double align when done with live preview mode
        if not live_preview:
            self.view.run_command("align_tab", {"user_input": user_input, "mode": mode})
