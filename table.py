import sublime
import sublime_plugin
import threading

class AlignTabClearMode(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        if view.is_scratch() or view.settings().get('is_widget'): return
        vid = view.id()
        print("Clear Table Mode!")
        if vid in AlignTabModeController.Mode:
            AlignTabModeController.Mode[vid] = False
        view.set_status("aligntab", "")


class AlignTabModeController(sublime_plugin.EventListener):
    # aligntab thread
    thread = None
    # register for table mode
    Mode = {}
    registered_actions = ["insert", "left_delete", "right_delete",
        "delete_word", "paste", "cut"]

    def on_modified(self, view):
        if view.is_scratch() or view.settings().get('is_widget'): return
        vid = view.id()
        if vid in AlignTabModeController.Mode and AlignTabModeController.Mode[vid]:
            cmdhist = view.command_history(0)
            # print(cmdhist)
            if cmdhist[0] not in self.registered_actions: return
            if self.thread:
                self.thread.cancel()
            self.thread = threading.Timer(0.2, lambda:
                view.run_command("align_tab",
                    {"user_input": "last_rexp", "mode": True}))
            self.thread.start()


    def on_text_command(self, view, cmd, args):
        if view.is_scratch() or view.settings().get('is_widget'): return
        vid = view.id()
        if vid in AlignTabModeController.Mode and AlignTabModeController.Mode[vid]:
            if cmd == "undo":
                view.run_command("soft_undo")
                return ("soft_undo", None)
            return None


    def on_query_context(self, view, key, operator, operand, match_all):
        if view.is_scratch() or view.settings().get('is_widget'): return
        vid = view.id()
        if key == 'align_tab_mode':
            if vid in AlignTabModeController.Mode:
                return AlignTabModeController.Mode[vid]
            else:
                return False

    # remove AlignTabModeController.Mode[vid] if file closes
    def on_close(self, view):
        vid = view.id()
        if vid in AlignTabModeController.Mode: AlignTabModeController.Mode.pop(vid)


