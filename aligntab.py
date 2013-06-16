import sublime
import sublime_plugin
import re, string, os, itertools, sys
if sys.version >= '3':
    from .pyparsing.pyparsing2 import *
else:
    from pyparsing.pyparsing import *

if not 'hist' in globals(): hist = []

def lister(option):
    output = []
    for i,x in enumerate(option):
        if type(x) == list:
            if i<len(option)-1 and option[i+1].isdigit():
                output+= lister(x*int(option[i+1]))
            else:
                output+= lister(x)
        elif not x.isdigit():
            output.append(x)
    return output

def parser(option):
    try:
        digits = Word('0123456789')
        star = Word('*').setParseAction( replaceWith("") )
        flag = Combine(Word('lcr',exact=1)+Optional(digits)+Optional('*'+digits)) | Combine(star+digits)
        nestedParens = nestedExpr('(', ')', content=flag)
        exp = OneOrMore(OneOrMore(flag) | nestedParens)+stringEnd
        output = []
        for item in lister(exp.parseString(option).asList()):
            m = re.match(r"([lcr][0-9]*)(?:\*([0-9]+))",item)
            if m:
                output += [m.group(1)]*int(m.group(2))
            else:
                output.append(item)

        return [item if len(item)>1 else item+"1" for item in output]
    except ParseException:
        pass


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
        view = self.view

        # insert history and reset index
        if not hist or user_input!= hist[-1]: hist.append(user_input)
        CycleAlignTabHistory.index = None

        user_input = get_named_pattern(user_input)

        #  ((?:[rlc][0-9]*(?:\*[0-9]+)?|\((?:[rlc][0-9]*)+\)(?:\*[0-9]+)?)*)
        m = re.match(r'(.+)/([0-9lcr\*\(\)]*)(?:(f[0-9]*))?$', user_input)

        regex = m.group(1) if m and (m.group(2) or m.group(3)) else user_input
        regex = "(" + regex + ")"

        option = parser(m.group(2)) if m and m.group(2) else ["l1"]
        if not option:
            regex = user_input
            option = ["l1"]

        # print(option)

        f = m.group(3) if m and m.group(3) else "f0"
        f = 1 if f == "f" else int(f[1:])


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