import sublime
import sublime_plugin

# VintageEX teaches me the following
class AlignTabHistory(sublime_plugin.TextCommand):
    HIST = []
    index = None
    def run(self, edit, backwards=False):
        if AlignTabHistory.index is None:
            AlignTabHistory.index = -1 if backwards else 0
        else:
            AlignTabHistory.index += -1 if backwards else 1

        if AlignTabHistory.index == len(AlignTabHistory.HIST) or \
            AlignTabHistory.index < -len(AlignTabHistory.HIST):
                AlignTabHistory.index = -1 if backwards else 0

        self.view.erase(edit, sublime.Region(0, self.view.size()))
        self.view.insert(edit, 0, AlignTabHistory.HIST[AlignTabHistory.index])

    @staticmethod
    def insert(user_input):
        if not AlignTabHistory.HIST or \
            (user_input!= AlignTabHistory.HIST[-1] \
                and user_input!= "last_rexp"):
            AlignTabHistory.HIST.append(user_input)
            AlignTabHistory.index = None

class AlignTabHistoryListener(sublime_plugin.EventListener):
    # restore History index
    def on_deactivated(self, view):
        if view.score_selector(0, 'text.aligntab') > 0:
            AlignTabHistory.index = None
