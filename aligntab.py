import sublime
import sublime_plugin
import re, sys
if sys.version >= '3':
    from .pyparsing import *
else:
    from pyparsing import *

if not 'hist' in globals(): hist = []

def parser(user_input):
    try:
        repeater = lambda t: list(t[0])*int(t[1]) if len(t)==2 else t[0]
        complete_jflag = lambda t: [[t[0],int(t[1])]] if len(t)==2 else [[t[0],1]]
        complete_fflag = lambda t: int(t[1]) if len(t)==2 else 1 if len(t)==1 else [None]
        digits = Word('0123456789')
        # justication flag
        jflag = (Word('lcr',exact=1)+Optional(digits)).setParseAction(complete_jflag)
        jflagr = (Group(jflag)+Optional(Suppress('*')+digits)).setParseAction(repeater)

        oExpr = Forward()
        nestedParens = (Suppress('(') + Group(oExpr) + Suppress(')')
                            +Optional(Suppress("*")+digits)).setParseAction(repeater)
        oExpr << OneOrMore(jflagr| nestedParens)

        fExpr = Optional('f'+Optional(digits)).setParseAction(complete_fflag)
        Inputparser = Regex(".+(?=/)")+Suppress("/")+Group(Optional(oExpr))+fExpr+stringEnd

        out = Inputparser.parseString(user_input).asList()
    except ParseException:
        out = None
    # print(out)
    regex = out[0] if (out and (out[1] or out[2])) else user_input
    option = out[1] if (out and out[1]) else [['l',1]]
    f = out[2] if out and out[2] else 0
    return [regex, option ,f]

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
    return user_input

class AlignTabCommand(sublime_plugin.TextCommand):

    def run(self, edit, user_input=None):
        if not user_input:
            v = self.view.window().show_input_panel('Align with regex:', '',
                    lambda x: self.view.run_command("align_tab",{"user_input":x}), None, None)
            v.set_syntax_file('Packages/AlignTab/AlignTab.hidden-tmLanguage')
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
        view = self.view

        # insert history and reset index
        if not hist or user_input!= hist[-1]: hist.append(user_input)
        CycleAlignTabHistory.index = None

        user_input = get_named_pattern(user_input)

        [regex, option, f] = parser(user_input)
        regex = '(' + regex + ')'

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
    index = None
    def run(self, edit, backwards=False):
        if CycleAlignTabHistory.index is None:
            CycleAlignTabHistory.index = -1 if backwards else 0
        else:
            CycleAlignTabHistory.index += -1 if backwards else 1

        if CycleAlignTabHistory.index == len(hist) or \
            CycleAlignTabHistory.index < -len(hist):
                CycleAlignTabHistory.index = -1 if backwards else 0

        self.view.erase(edit, sublime.Region(0, self.view.size()))
        self.view.insert(edit, 0, hist[CycleAlignTabHistory.index])

class HistoryIndexRestorer(sublime_plugin.EventListener):
    def on_deactivated(self, view):
        if view.score_selector(0, 'text.aligntab') > 0:
            CycleAlignTabHistory.index = None