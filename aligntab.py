import sublime
import sublime_plugin
import re, sys

if not 'MODE' in globals(): MODE = {}
if not 'HIST' in globals(): HIST = []

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

def get_named_pattern(user_input):
    patterns = sublime.load_settings('AlignTab.sublime-settings').get('named_patterns', {})
    user_input = patterns[user_input] if user_input in patterns else user_input
    user_input = HIST[-1] if HIST and user_input == 'last_rexp' else user_input
    return user_input

class AlignTabCommand(sublime_plugin.TextCommand):
    # Default the live_enabled setting so that if it doesn't get loaded nothing will break
    live_enabled = False
    
    def run(self, edit, user_input=None, mode=False, event_type=False):
        if not event_type and user_input: 
            # Set live_change_made to false to prevent problems with context menu
            self.live_change_made = False
            # Event type needed to prevent infinite loop in show_input_panel()
            event_type = "done"
        
        if not event_type:
            v = self.view.window().show_input_panel('Align By RegEx:', '',
                    # On Done
                    lambda x: self.view.run_command("align_tab",{"user_input":x, "mode":mode, "event_type":"done"}), 
                    # On Change
                    lambda x: self.on_change(x, mode),
                    # On Canel
                    lambda: self.on_change("", mode) )
            v.set_syntax_file('Packages/AlignTab/AlignTab.hidden-tmLanguage')
            v.settings().set('is_widget', True)
            v.settings().set('gutter', False)
            v.settings().set('rulers', [])
            self.live_change_made = False
            # Load the live_preview setting
            AlignTabCommand.live_enabled = sublime.load_settings('AlignTab.sublime-settings').get('live_preview')
            # Find out what the cap is on line count
            AlignTabCommand.live_preview_limit = sublime.load_settings('AlignTab.sublime-settings').get('live_preview_limit')
        else:
            self.align_tab(edit, user_input, mode, event_type)

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

    def on_change(self, user_input, mode=False):
        # Don't do anything if we're not live
        if not AlignTabCommand.live_enabled:
            return
        # Undo the previous change if needed
        if(self.live_change_made):
            self.view.run_command("undo")
        # Run the align command
        self.view.run_command("align_tab",{"user_input":user_input, "mode":mode, "event_type":"change"})        
        
    def prev_next_match(self, regex, f):
        # it is used to check whether table mode should be disabled
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


    def align_tab(self, edit, user_input, mode, event_type):
        view = self.view
        vid = view.id()
        
        # Don't update history if this is a live change
        if event_type != "change":
            # insert history and reset index
            if not HIST or (user_input!= HIST[-1] and user_input!= "last_rexp"): HIST.append(user_input)
            AlignTabHistory.index = None
        # If live is enabled, then don't re-change the text. We're done
        if (AlignTabCommand.live_enabled) and (self.live_change_made) and (event_type == "done"): return
        
        user_input = get_named_pattern(user_input)
        [regex, option, f] = input_parser(user_input)
        regex = '(' + regex + ')'

        rows = []
        colwidth = []
        # do not strip \t if translate_tabs_to_spaces is false (which is the default)
        strip_char = ' ' if not view.settings().get("translate_tabs_to_spaces", False) else None
        self.expand_sel(regex, option, f , rows, colwidth, strip_char)
        rows = sorted(set(rows))
        # Bail if the cap exceeds the number of rows permitted
        if (event_type == "change") and (len(rows) > AlignTabCommand.live_preview_limit): return
        # If rows were found, then note that we have an undo due
        self.live_change_made = not not rows
        global MODE
        if rows:
            if mode:
                MODE[vid] = True
                view.set_status("AlignTab", "[Table Mode]")
        else:
            # this means no selection was detected to contain the regex, therefore we check previous line and next line for each cursor
            if mode and not all(list(self.prev_next_match(regex, f))):
                MODE[vid] = False
                view.set_status("AlignTab", "")
            return

        indentation = min([re.match("^(\s*)",
                view.substr(view.line(view.text_point(row,0)))).group(1) for row in rows])

        for row in reversed(rows):
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

                # oldpt is used to reset cursor position, since view.insert will change cursor's location

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


class AlignTabClearMode(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        if view.is_scratch() or view.settings().get('is_widget'): return
        vid = view.id()
        global MODE
        print("Clear Table Mode!")
        if vid in MODE:
            MODE[vid] = False
            view.set_status("AlignTab", "")

class AlignTabUndo(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        if view.is_scratch() or view.settings().get('is_widget'): return
        vid = view.id()
        global MODE
        if vid in MODE:
            MODE[vid] = False
            view.run_command("undo")
            view.run_command("undo")
            MODE[vid] = True

class AlignTabUpdater(sublime_plugin.EventListener):
    # Table mode
    def on_modified(self, view):
        if view.is_scratch() or view.settings().get('is_widget'): return
        cmdhist = view.command_history(0)
        if cmdhist[0] not in ["insert", "left_delete", "right_delete", "paste", "cut"]: return
        if cmdhist[0] == "insert" and cmdhist[1] == {'characters': ' '}: return
        vid = view.id()
        global MODE
        if vid in MODE:
            if MODE[vid]:
                view.run_command("align_tab", {"user_input": "last_rexp", "mode": True})

    def on_query_context(self, view, key, operator, operand, match_all):
        if view.is_scratch() or view.settings().get('is_widget'): return
        vid = view.id()
        if key == 'align_tab_mode':
            global MODE
            if vid in MODE:
                return MODE[vid]
            else:
                return False

    # restore History index
    def on_deactivated(self, view):
        if view.score_selector(0, 'text.aligntab') > 0:
            AlignTabHistory.index = None

    # remove MODE[vid] if file closes
    def on_close(self, view):
        vid = view.id()
        if vid in MODE: MODE.pop(vid)

# VintageEX teaches me the following
class AlignTabHistory(sublime_plugin.TextCommand):
    index = None
    def run(self, edit, backwards=False):
        if AlignTabHistory.index is None:
            AlignTabHistory.index = -1 if backwards else 0
        else:
            AlignTabHistory.index += -1 if backwards else 1

        if AlignTabHistory.index == len(HIST) or \
            AlignTabHistory.index < -len(HIST):
                AlignTabHistory.index = -1 if backwards else 0

        self.view.erase(edit, sublime.Region(0, self.view.size()))
        self.view.insert(edit, 0, HIST[AlignTabHistory.index])

