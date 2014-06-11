import sublime
import sublime_plugin
import threading

def toogle_table_mode(view, on=True):
    if on:
        view.settings().set("AlignTabTableMode", True)
        view.set_status("aligntab", "[Table Mode]")
    else:
        view.settings().erase("AlignTabTableMode")
        view.set_status("aligntab", "")

class AlignTabModeController(sublime_plugin.EventListener):
    # aligntab thread
    thread = None
    # register for table mode
    registered_actions = ["insert", "left_delete", "right_delete",
        "delete_word", "paste", "cut"]

    def on_modified(self, view):
        if view.is_scratch() or view.settings().get('is_widget'): return
        vid = view.id()
        if self.table_mode(view):
            cmdhist = view.command_history(0)
            # print(cmdhist)
            if cmdhist[0] not in self.registered_actions: return
            if self.thread:
                self.thread.cancel()
            self.thread = threading.Timer(0.2, lambda:
                view.run_command("align_tab",
                    {"user_input": "last_regex", "mode": True}))
            self.thread.start()


    def on_text_command(self, view, cmd, args):
        if view.is_scratch() or view.settings().get('is_widget'): return
        vid = view.id()
        if self.table_mode(view):
            if cmd == "undo":
                view.run_command("soft_undo")
                return ("soft_undo", None)
            return None

    def table_mode(self, view):
        return view.settings().has("AlignTabTableMode")


class AlignTabClearMode(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        if view.is_scratch() or view.settings().get('is_widget'): return
        toogle_table_mode(view, False)
