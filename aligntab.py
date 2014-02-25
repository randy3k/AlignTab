import sublime
import sublime_plugin
import re, sys
import time
import threading

def input_parser(user_input):
    m = re.match(r"(.+)/([lcr*()0-9]*)(f[0-9]*)?", user_input)

    if m and (m.group(2) or m.group(3)):
        regex = m.group(1)
        option = m.group(2)
        f = m.group(3)
    else:
        # print("No options!")
        return [user_input, [['l', 1]], 0]

    try:
        # for option
        rParan = re.compile(r"\(([^())]*)\)\*([0-9]+)")
        while True:
            if not rParan.search(option): break
            for r in rParan.finditer(option):
                option = option.replace(r.group(0), r.group(1)*int(r.group(2)),1)

        for r in re.finditer(r"([lcr][0-9]*)\*([0-9]+)", option):
            option = option.replace(r.group(0), r.group(1)*int(r.group(2)),1)

        option = re.findall(r"[lcr][0-9]*", option)
        option = list(map(lambda x: [x[0], 1] if len(x)==1 else [x[0], int(x[1:])], option))
        option = option if option else [['l', 1]]

        # for f
        f = 0 if not f else 1 if len(f)==1 else int(f[1:])
    except:
        [regex, option ,f]= [user_input, [['l', 1]], 0]

    return [regex, option ,f]

def update_colwidth(colwidth, content, option, strip_char):
    thiscolwidth = [len(c.strip(strip_char)) if i>0 else len(c.rstrip(strip_char).lstrip()) for i, c in enumerate(content)]
    for i,w in enumerate(thiscolwidth):
        if i<len(colwidth):
            colwidth[i] = max(colwidth[i], w)
        else:
            colwidth.append(w)


def fill_spaces(content, colwidth, option, strip_char):
    for j in range(len(content)):
        op = option[j % len(option)]
        content[j] = content[j].strip(strip_char)
        align = op[0]
        spaceafter = " "*op[1] if j<len(content)-1 else ""
        fill = colwidth[j]-len(content[j])
        if align=='l':
            content[j] = content[j] + " "*fill + spaceafter
        elif align == 'r':
            content[j] = " "*fill + content[j] + spaceafter
        elif align == 'c':
            lfill = " "*int(fill/2)
            rfill = " "*(fill-int(fill/2))
            content[j] = lfill + content[j] + rfill + spaceafter

def get_named_pattern(user_input):
    patterns = sublime.load_settings('AlignTab.sublime-settings').get('named_patterns', {})
    user_input = patterns[user_input] if user_input in patterns else user_input
    user_input = AlignTabHistory.HIST[-1] if AlignTabHistory.HIST and user_input == 'last_rexp' else user_input
    return user_input

class AlignTabCommand(sublime_plugin.TextCommand):
    Mode = {}
    def run(self, edit, user_input=None, mode=False, live_preview=False):
        view = self.view
        vid = view.id()
        if not user_input:
            self.aligned = False
            v = self.view.window().show_input_panel('Align By RegEx:', '',
                    # On Done
                    lambda x: self.on_done(x, mode, live_preview),
                    # On Change
                    lambda x: self.on_change(x) if live_preview else None,
                    # On Cancel
                    lambda: self.on_change(None) if live_preview else None )

            v.set_syntax_file('Packages/AlignTab/AlignTab.hidden-tmLanguage')
            v.settings().set('is_widget', True)
            v.settings().set('gutter', False)
            v.settings().set('rulers', [])

        else:
            if user_input:
                # do not double align when done with live preview mode
                if live_preview is not "done":
                    self.align_tab(edit, user_input, mode, live_preview)

                if self.aligned:
                    if mode:
                        self.toogle_table_mode(True)
                    else:
                        sublime.status_message("")
                else:
                    if mode and not all(list(self.prev_next_match(user_input))):
                        self.toogle_table_mode(False)
                    else:
                        sublime.status_message("[Pattern not Found]")

    def on_change(self, user_input):
        view = self.view
        vid = view.id()
        # Undo the previous change if needed
        if self.aligned:
            self.view.run_command("soft_undo")
            self.aligned = False
        if user_input:
            self.view.run_command("align_tab",{"user_input":user_input, "live_preview":True})

    def on_done(self, user_input, mode, live_preview):
        view = self.view
        AlignTabHistory.insert(user_input)
        if not live_preview:
            self.view.run_command("align_tab",{"user_input":user_input, "mode":mode})

    def toogle_table_mode(self, on=True):
        view = self.view
        vid = view.id()
        if on:
            AlignTabCommand.Mode[vid] = True
            view.set_status("aligntab", "[Table Mode]")
        else:
            AlignTabCommand.Mode[vid] = False
            view.set_status("aligntab", "")

    def get_line_content(self, regex, f, row):
        view = self.view
        line = view.line(view.text_point(row,0))
        return [s for s in re.split(regex,view.substr(line),f)]

    def expand_sel(self, regex, option, f, rows, colwidth, strip_char):
        view = self.view
        lastrow = view.rowcol(view.size())[0]

        for sel in view.sel():
            for line in view.lines(sel):
                thisrow = view.rowcol(line.begin())[0]
                if (thisrow in rows): continue
                content = self.get_line_content(regex, f, thisrow)
                if len(content)<=1: continue
                update_colwidth(colwidth, content, option, strip_char)
                rows.append(thisrow)

            if sel.empty():
                thisrow = view.rowcol(sel.begin())[0]
                if not (thisrow in rows): continue
                beginrow = endrow = thisrow
                while endrow+1<=lastrow and not (endrow+1 in rows):
                    content = self.get_line_content(regex, f, endrow+1)
                    if len(content)<=1: break
                    update_colwidth(colwidth, content, option, strip_char)
                    endrow = endrow+1
                    rows.append(endrow)
                while beginrow-1>=0 and not (beginrow-1 in rows):
                    content = self.get_line_content(regex, f, beginrow-1)
                    if len(content)<=1: break
                    update_colwidth(colwidth, content, option, strip_char)
                    beginrow = beginrow-1
                    rows.append(beginrow)

    def prev_next_match(self, user_input):
        # it is used to check whether table mode should be disabled
        user_input = get_named_pattern(user_input)
        [regex, option, f] = input_parser(user_input)
        regex = '(' + regex + ')'
        view = self.view
        lastrow = view.rowcol(view.size())[0]
        rows = []
        for sel in view.sel():
            for line in view.lines(sel):
                rows.append(view.rowcol(line.begin())[0])
        rows = list(set(rows))
        for row in rows:
            if row-1>=0 and len(self.get_line_content(regex, f, row-1))>1:
                yield True
            elif row+1<=lastrow and len(self.get_line_content(regex, f, row+1))>1:
                yield True
            else:
                yield False


    def align_tab(self, edit, user_input, mode, live_preview):
        view = self.view
        vid  = view.id()

        user_input = get_named_pattern(user_input)
        [regex, option, f] = input_parser(user_input)
        regex = '(' + regex + ')'

        # test validity of regex
        try:
            re.compile(regex)
        except:
            self.aligned = False
            return

        rows = []
        colwidth = []
        # do not strip \t if translate_tabs_to_spaces is false (which is the default)
        strip_char = ' ' if not view.settings().get("translate_tabs_to_spaces", False) else None
        self.expand_sel(regex, option, f , rows, colwidth, strip_char)
        rows = sorted(set(rows))
        if rows:
            self.aligned = True
        else:
            self.aligned = False
            return

        indentation = min([re.match("^(\s*)",
                view.substr(view.line(view.text_point(row,0)))).group(1) for row in rows])

        # for table mode, we need to reset the cursor positions
        cursor_rows = []
        for s in view.sel():
            if s.empty:
                cursor_rows += range(view.rowcol(s.begin())[0],view.rowcol(s.end())[0]+1)
        for row in reversed(rows):
            if mode and row in cursor_rows:
                # if this row contains cursors, then need to reset cursor positions in a complicated way
                # view.insert will change cursor's location
                # oldpt is used to reset cursor position

                content = self.get_line_content(regex, f, row)
                # the last col
                begin = view.line(view.text_point(row, 0)).end()
                for i, c in reversed(list(enumerate(content))):
                    # option cycles through the columns
                    op = option[i % len(option)]
                    # begin of current cell
                    begin = begin-len(c)
                    lenc = len(c.strip(strip_char)) if i>0 else len(c.rstrip(strip_char).lstrip())
                    se = len(c) - len(c.rstrip(strip_char))
                    sb = len(c)-lenc-se

                    if op[0] == "l":
                        fill = colwidth[i]-lenc+op[1] if i != len(content)-1 else 0
                        oldpt = [min(s.end()-sb,begin+lenc+fill) if lenc>0 else begin \
                                    for s in view.sel() if s.empty() and begin+sb+lenc<=s.end()<=begin+sb+lenc+se]
                        view.erase(edit, sublime.Region(begin,begin+sb))
                        view.erase(edit, sublime.Region(begin+lenc,begin+lenc+se))
                        view.insert(edit, begin+lenc, " "*(fill))
                        if oldpt:
                            view.sel().subtract(sublime.Region(begin+lenc, begin+lenc+fill))
                            for s in [sublime.Region(b,b) for b in oldpt]: view.sel().add(s)

                    if op[0] == "r":
                        fill = colwidth[i]-lenc
                        oldpt = [min(s.end()-sb+fill,begin+lenc+fill+op[1]) if lenc>0 else begin \
                                    for s in view.sel() if s.empty() and begin+sb+lenc<=s.end()<=begin+sb+lenc+se]
                        view.erase(edit, sublime.Region(begin,begin+sb))
                        view.erase(edit, sublime.Region(begin+lenc,begin+lenc+se))
                        if i != len(content)-1: view.insert(edit, begin+lenc, " "*op[1])
                        view.insert(edit, begin, " "*fill)
                        if oldpt:
                            view.sel().subtract(sublime.Region(begin+fill+lenc, begin+fill+lenc+op[1]))
                            for s in [sublime.Region(b,b) for b in oldpt]: view.sel().add(s)

                        if op[0] == "c":
                            lfill = int((colwidth[i]-lenc)/2)
                            rfill = colwidth[i]-lenc-lfill+op[1] if i != len(content)-1 else 0
                            oldpt = [min(s.end()-sb+lfill,begin+lenc+lfill+rfill) if lenc>0 else begin\
                                        for s in view.sel() if s.empty() and begin+sb+lenc<=s.end()<=begin+sb+lenc+se]
                            view.erase(edit, sublime.Region(begin,begin+sb))
                            view.erase(edit, sublime.Region(begin+lenc,begin+lenc+se))
                            view.insert(edit, begin, " "*lfill)
                            view.insert(edit, begin+lfill+lenc, " "*rfill)
                            if oldpt:
                                view.sel().subtract(sublime.Region(begin+lfill+lenc, begin+lenc+lfill+rfill))
                                for s in [sublime.Region(b,b) for b in oldpt]: view.sel().add(s)

                view.insert(edit, view.text_point(row,0), indentation)
            else:
                # fast implementation, but cursor positions will change
                line = view.line(view.text_point(row,0))
                content = self.get_line_content(regex, f, row)
                fill_spaces(content, colwidth, option, strip_char)
                view.replace(edit,line, (indentation + "".join(content)).rstrip(strip_char))


class AlignTabClearMode(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        if view.is_scratch() or view.settings().get('is_widget'): return
        vid = view.id()
        print("Clear Table Mode!")
        if vid in AlignTabCommand.Mode:
            AlignTabCommand.Mode[vid] = False
        view.set_status("aligntab", "")


class AlignTabUpdater(sublime_plugin.EventListener):
    # aligntab thread
    thread = None

    # table mode trigger
    def on_modified(self, view):
        if view.is_scratch() or view.settings().get('is_widget'): return
        vid = view.id()
        if vid in AlignTabCommand.Mode and AlignTabCommand.Mode[vid]:
            cmdhist = view.command_history(0)
            # print(cmdhist)
            if cmdhist[0] not in ["insert", "left_delete", "right_delete", "delete_word", "paste", "cut"]: return
            # if cmdhist[0] == "insert" and cmdhist[1] == {'characters': ' '}: return
            if self.thread:
                self.thread.cancel()
            self.thread = threading.Timer(0.2, lambda:
                                view.run_command("align_tab", {"user_input": "last_rexp", "mode": True}))
            self.thread.start()


    def on_text_command(self, view, cmd, args):
        if view.is_scratch() or view.settings().get('is_widget'): return
        vid = view.id()
        if vid in AlignTabCommand.Mode and AlignTabCommand.Mode[vid]:
            if cmd == "undo":
                view.run_command("soft_undo")
                return ("soft_undo", None)
            return None


    def on_query_context(self, view, key, operator, operand, match_all):
        if view.is_scratch() or view.settings().get('is_widget'): return
        vid = view.id()
        if key == 'align_tab_mode':
            if vid in AlignTabCommand.Mode:
                return AlignTabCommand.Mode[vid]
            else:
                return False

    # restore History index
    def on_deactivated(self, view):
        if view.score_selector(0, 'text.aligntab') > 0:
            AlignTabHistory.index = None

    # remove AlignTabCommand.Mode[vid] if file closes
    def on_close(self, view):
        vid = view.id()
        if vid in AlignTabCommand.Mode: AlignTabCommand.Mode.pop(vid)


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
        if not AlignTabHistory.HIST or (user_input!= AlignTabHistory.HIST[-1] and user_input!= "last_rexp"):
            AlignTabHistory.HIST.append(user_input)
            AlignTabHistory.index = None

