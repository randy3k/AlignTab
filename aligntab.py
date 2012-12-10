import sublime
import sublime_plugin
import re, string, os


if not 'HIST' in globals(): HIST = []

def colwidth(lines_content):
    width = [0]*max([len(lc) for lc in lines_content])
    for lc in lines_content:
        for i,x in enumerate(lc):
            if width[i]<len(x): width[i] = len(x)
    return width

def fill_spaces(lines_content, option):
    width = colwidth(lines_content)
    # can make more efficient by pre-computing variable to
    for k in range(len(lines_content)):
        for j in range(len(lines_content[k])):
            to = option[j % len(option)]
            spaceafter = " "*int(to[1:]) if j<len(lines_content[k])-1 else ""
            fill = width[j]-len(lines_content[k][j])
            if to[0]=='l':
                lines_content[k][j] = lines_content[k][j] + " "*fill + spaceafter
            elif to[0] == 'r':
                lines_content[k][j] = " "*fill + lines_content[k][j] + spaceafter
            elif to[0] == 'c':
                lfill = " "*int(fill/2)
                rfill = " "*(fill-int(fill/2))
                lines_content[k][j] = lfill + lines_content[k][j] + rfill + spaceafter

    return lines_content

class AlignTabCommand(sublime_plugin.TextCommand):

    def run(self, _, user_input=None):
        if not user_input:
            v = self.view.window().show_input_panel('Align with regex:', '',
                    self.align_tab, None, None)
            # print os.getcwd()
            v.set_syntax_file('Packages/AlignTab/AlignTab.tmLanguage')
            v.settings().set('gutter', False)
            v.settings().set('rulers', [])
        else:
            self.align_tab(user_input)

    def expand_sel(self, regex):
        view = self.view
        lastrow = view.rowcol(view.size())[0]
        rows = []
        for sel in view.sel():
            if sel.begin()!=sel.end(): continue
            saved_pt =sel.begin()
            row = view.rowcol(saved_pt)[0]
            if row in rows: continue
            if not re.search(regex, view.substr(view.line(saved_pt))): continue
            beginrow = endrow = row
            rows.append(row)
            while endrow+1<=lastrow and not (endrow+1 in rows):
                if re.search(regex, view.substr(view.line(view.text_point(endrow+1,0)))):
                    endrow = endrow+1
                    rows.append(endrow)
                else: break
            while beginrow-1>=0 and not (beginrow-1 in rows):
                if re.search(regex, view.substr(view.line(view.text_point(beginrow-1,0)))):
                    beginrow = beginrow-1
                    rows.append(beginrow)
                else: break
        if not rows: return
        for row in rows:
            view.sel().add(view.line(view.text_point(row,0)))

    def align_tab(self, user_input):
        # insert history and reset index
        if not HIST or user_input!= HIST[-1]: HIST.append(user_input)
        CycleAlignTabHistory.INDEX = None

        m = re.match('(.+)/((?:[rlc][0-9]*)+)?(?:(f[0-9]*))?$', user_input)
        regex = m.group(1) if m else user_input
        option = m.group(2) if m and m.group(2) else "l1"
        f = m.group(3) if m and m.group(3) else "f0"
        option = [pat if len(pat)>1 else pat+"1" for pat in re.findall('[rlc][0-9]*', option)]
        f = "f1" if f == "f" else f
        view = self.view
        print regex,option,f
        self.expand_sel(regex)
        view.run_command("split_selection_into_lines")
        lines = []
        lines_content = []
        for sel in view.sel():
            for line in view.lines(sel):
                if line in lines: continue
                content = [s.strip() for s in re.split("("+regex+")",view.substr(line),int(f[1:])) ]
                if len(content)>1:
                    lines.append(line)
                    lines_content.append(content)
        if not lines_content: return

        lines_content = fill_spaces(lines_content, option)
        spacebefore = re.match("^(\s*)", view.substr(view.line(lines[0].begin()))).group(1)
        view.sel().clear()
        edit = view.begin_edit()
        for k in reversed(range(len(lines))):
            view.replace(edit,lines[k], spacebefore+"".join(lines_content[k]))
            view.sel().add(view.line(lines[k].begin()))

        view.end_edit(edit)
        # print "\n".join(["".join(lc) for lc in lines_content])



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
        if view.score_selector(0, 'text.autotab') > 0:
            CycleAlignTabHistory.INDEX = None