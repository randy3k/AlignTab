import sublime
import sublime_plugin
import re, string, os, itertools


if not 'HIST' in globals(): HIST = []


def update_colwidth(colwidth, content):
    thiscolwidth = [len(s) for s in content]
    for i,w in enumerate(thiscolwidth):
        if i<len(colwidth):
            colwidth[i] = max(colwidth[i], w)
        else:
            colwidth.append(w)

def fill_spaces(content, colwidth, option):
    for j in range(len(content)):
        op = option[j % len(option)]
        align = op[0]
        spaceafter = " "*int(op[1:]) if j<len(content)-1 else ""
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
    return user_input

class AlignTabCommand(sublime_plugin.TextCommand):

    def run(self, edit, user_input=None):
        if not user_input:
            v = self.view.window().show_input_panel('Align with regex:', '',
                    lambda x: self.view.run_command("align_tab",{"user_input":x}), None, None)
            # print os.getcwd()
            v.set_syntax_file('Packages/AlignTab/AlignTab.tmLanguage')
            v.settings().set('gutter', False)
            v.settings().set('rulers', [])
        else:
            self.align_tab(edit, user_input)

    def get_line_content(self, regex, f, row):
        view = self.view
        line = view.line(view.text_point(row,0))
        return [s.strip() for s in re.split(regex,view.substr(line),f)]

    def expand_sel(self, regex, f, rows, colwidth):
        view = self.view
        lastrow = view.rowcol(view.size())[0]
        for sel in view.sel():
            for line in view.lines(sel):
                thisrow = view.rowcol(line.begin())[0]
                if (thisrow in rows): continue
                content = self.get_line_content(regex, f, thisrow)
                if len(content)<=1: continue
                update_colwidth(colwidth, content)
                rows.append(thisrow)

            if sel.begin()==sel.end():
                thisrow = view.rowcol(sel.begin())[0]
                if not (thisrow in rows): continue
                beginrow = endrow = thisrow
                while endrow+1<=lastrow and not (endrow+1 in rows):
                    content = self.get_line_content(regex, f, endrow+1)
                    if len(content)<=1: break
                    update_colwidth(colwidth, content)
                    endrow = endrow+1
                    rows.append(endrow)
                while beginrow-1>=0 and not (beginrow-1 in rows):
                    content = self.get_line_content(regex, f, beginrow-1)
                    if len(content)<=1: break
                    update_colwidth(colwidth, content)
                    beginrow = beginrow-1
                    rows.append(beginrow)


    def align_tab(self, edit, user_input):
        # insert history and reset index
        if not HIST or user_input!= HIST[-1]: HIST.append(user_input)
        CycleAlignTabHistory.INDEX = None

        user_input = get_named_pattern(user_input)

        m = re.match(r'(.+)/((?:[rlc][0-9]*(?:\*[0-9]+)?|\((?:[rlc][0-9]*)+\)(?:\*[0-9]+)?)*)(?:(f[0-9]*))?$', user_input)
        regex = m.group(1) if m and (m.group(2) or m.group(3)) else user_input
        regex = "(" + regex + ")"
        option = m.group(2) if m and m.group(2) else "l1"
        # replace (...)*n by repeating (...) n times
        for tri in re.findall(r'(\(((?:[rlc][0-9]*)+)\)(?:\*([0-9]+))?)', option):
            option = option.replace(tri[0], tri[1]*(int(tri[2]) if tri[2] else 1), 1)
        # replace [rlc]*n by repeating n times
        for tri in re.findall(r'(([rlc][0-9]*)(?:\*([0-9]+))?)', option):
            option = option.replace(tri[0], tri[1]*(int(tri[2]) if tri[2] else 1), 1)
        # break the option into list
        option = [op if len(op)>1 else op+"1" for op in re.findall(r'[rlc][0-9]*', option)]

        f = m.group(3) if m and m.group(3) else "f0"
        f = 1 if f == "f" else int(f[1:])
        view = self.view

        rows = []
        colwidth = []
        self.expand_sel(regex, f , rows, colwidth)
        rows = sorted(set(rows))
        if not rows: return

        spacebefore = min([re.match("^(\s*)", view.substr(view.line(view.text_point(row,0)))).group(1) for row in rows])
        for row in reversed(rows):
            line = view.line(view.text_point(row,0))
            content = [s.strip() for s in re.split(regex,view.substr(line),f) ]
            fill_spaces(content, colwidth, option)
            view.replace(edit,line, (spacebefore+"".join(content)).rstrip())


# VintageEX teaches me the following
class CycleAlignTabHistory(sublime_plugin.TextCommand):
    INDEX = None
    def run(self, edit, backwards=False):
        if CycleAlignTabHistory.INDEX is None:
            CycleAlignTabHistory.INDEX = -1 if backwards else 0
        else:
            CycleAlignTabHistory.INDEX += -1 if backwards else 1

        if CycleAlignTabHistory.INDEX == len(HIST) or \
            CycleAlignTabHistory.INDEX < -len(HIST):
                CycleAlignTabHistory.INDEX = -1 if backwards else 0

        self.view.erase(edit, sublime.Region(0, self.view.size()))
        self.view.insert(edit, 0, HIST[CycleAlignTabHistory.INDEX])

class HistoryIndexRestorer(sublime_plugin.EventListener):
    def on_deactivated(self, view):
        # due to views loading asynchronously, do not restore history index
        # .on_activated(), but here instead. otherwise, the .score_selector()
        # call won't yield the desired results.
        if view.score_selector(0, 'text.aligntab') > 0:
            CycleAlignTabHistory.INDEX = None