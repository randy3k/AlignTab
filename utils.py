import sublime
import sublime_plugin
import os


class AlignTabEditSettings(sublime_plugin.WindowCommand):
    def run(self, **kwargs):
        STP = sublime.packages_path()
        STPA = os.path.join(STP, "User", "AlignTab")
        if not os.path.exists(STPA):
            os.makedirs(STPA)

        self.window.run_command("edit_settings", kwargs)
