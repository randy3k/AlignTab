import sublime
import sublime_plugin
import re
from .wclen import wclen

class Aligner:
    def __init__(self, view, regex, flag, f):
        self.view = view
        self.regex = regex
        self.flag = flag
        self.f = f
        self.strip_char = ' ' if not view.settings().get("translate_tabs_to_spaces", False) else None
        self.rows = []
        self.colwidth = []

    def get_line(self, row):
        view = self.view
        return view.substr(view.line(view.text_point(row,0)))

    def get_cells(self, row):
        view = self.view
        content = [s for s in re.split(self.regex, self.get_line(row), self.f)]
        # remove indentation
        if len(content)>1:
            content[0] = content[0].lstrip()
        # remove spaces
        content = [c.strip(self.strip_char) for c in content]
        return content

    def update_colwidth(self, content):
        thiscolwidth = [wclen(c) for c in content]
        for i,w in enumerate(thiscolwidth):
            if i<len(self.colwidth):
                self.colwidth[i] = max(self.colwidth[i], w)
            else:
                self.colwidth.append(w)

    def include_line(self, row):
        content = self.get_cells(row)
        if len(content)<=1: return False
        self.update_colwidth(content)
        self.rows.append(row)
        return True

    def expand_selections(self):
        view = self.view
        lastrow = view.rowcol(view.size())[0]

        for sel in view.sel():
            for line in view.lines(sel):
                thisrow = view.rowcol(line.begin())[0]
                if thisrow in self.rows: continue
                if not self.include_line(thisrow): continue

            if sel.empty():
                thisrow = view.rowcol(sel.begin())[0]
                if thisrow not in self.rows: continue
                beginrow = endrow = thisrow
                while endrow+1<=lastrow and not (endrow+1 in self.rows):
                    if not self.include_line(endrow+1): break
                    endrow = endrow+1
                while beginrow-1>=0 and not (beginrow-1 in self.rows):
                    if not self.include_line(beginrow-1): break
                    beginrow = beginrow-1

        self.rows = sorted(set(self.rows))

    def fill_spaces(self, content):
        for k in range(len(content)):
            if self.colwidth[k] == 0: continue
            thisf = self.flag[k % len(self.flag)]
            align = thisf[0]
            pedding = " "*thisf[1] if k<len(content)-1 else ""
            fill = self.colwidth[k]-wclen(content[k])
            if align=='l':
                content[k] = content[k] + " "*fill + pedding
            elif align == 'r':
                content[k] = " "*fill + content[k] + pedding
            elif align == 'c':
                lfill = " "*int(fill/2)
                rfill = " "*(fill-int(fill/2))
                content[k] = lfill + content[k] + rfill + pedding

    def get_span(self, row):
        # it is used to reset cursors in table mode
        view = self.view
        line = self.get_line(row)
        p = [m.span() for m in re.finditer(self.regex, line)]
        if self.f>0: p = p[0:self.f]
        p.append((len(line),None))
        cell = [(0, p[0][0])]
        for i in range(len(p)-1):
            cell.append(p[i])
            cell.append((p[i][1],p[i+1][0]))
        trimcell = []
        s = 0
        for c in cell:
            cellcontent = line[c[0]:c[1]]
            b = s + wclen(cellcontent.rstrip(self.strip_char))
            a = b - wclen(cellcontent.strip(self.strip_char))
            trimcell.append((a, b))
            s = s + wclen(cellcontent)
        return trimcell

    def prev_next_match(self):
        # it is used to check whether table mode should be disabled
        view = self.view
        lastrow = view.rowcol(view.size())[0]
        rows = []
        for sel in view.sel():
            for line in view.lines(sel):
                rows.append(view.rowcol(line.begin())[0])
        rows = list(set(rows))
        for row in rows:
            if len(self.get_cells(row))>1:
                continue
            elif row-1>=0 and len(self.get_cells(row-1))>1:
                continue
            elif row+1<=lastrow and len(self.get_cells(row+1))>1:
                continue
            else:
                return False
        return True

    def reset_cursor(self, row, old_span, cursor):
        view = self.view
        # reset cursors' location
        new_span = self.get_span(row)
        for s in view.sel():
            if s.empty and view.rowcol(s.end())[0]==row: view.sel().subtract(s)
        for cur in cursor:
            for i, c in reversed(list(enumerate(old_span))):
                if c[0]<= cur:
                    if cur<=c[1]:
                        newcur = cur-c[0]+new_span[i][0]
                    else:
                        newcur = c[1]-c[0]+new_span[i][0]
                    break
            pt = view.text_point(row,newcur)
            view.sel().add(sublime.Region(pt,pt))

    def replace_selections(self, edit, mode):
        view = self.view

        indentation = min([re.match("^(\s*)", self.get_line(row)).group(1) for row in self.rows])
        cursor_rows = set([view.rowcol(s.end())[0] for s in view.sel() if s.empty])

        for row in reversed(self.rows):
            if mode and row in cursor_rows:
                # if this row contains cursors, record their locations
                span = self.get_span(row)
                cursor = [view.rowcol(s.end())[1] for s in view.sel() if s.empty and view.rowcol(s.end())[0]==row]

            content = self.get_cells(row)
            self.fill_spaces(content)
            line = view.line(view.text_point(row,0))
            view.replace(edit, line, (indentation + "".join(content).rstrip(self.strip_char)))

            if mode and row in cursor_rows:
                self.reset_cursor(row, span, cursor)

    def run(self, edit, mode=False):
        # check if regex is valid
        try:
            re.compile(self.regex)
        except:
            return False
        self.expand_selections()

        if not self.rows: return False

        self.replace_selections(edit, mode)
        return True
