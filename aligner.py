import sublime
import re
from .parser import input_parser
from .wclen import wclen
from .table import get_table_rows, set_table_rows


class Aligner:
    def __init__(self, view, user_input, mode=False):
        [regex, flag, f] = input_parser(user_input)
        regex = '(' + regex + ')'
        self.view = view
        self.regex = regex
        self.flag = flag
        self.f = f
        if view.settings().get("translate_tabs_to_spaces", False):
            self.strip_char = None
        else:
            self.strip_char = ' '
        self.rows = []
        self.colwidth = []
        self.mode = mode

    def get_flag(self, col):
        return self.flag[col % len(self.flag)]

    def get_line(self, row):
        view = self.view
        return view.substr(view.line(view.text_point(row, 0)))

    def get_cells(self, row):
        content = [s for s in re.split(self.regex, self.get_line(row), self.f)]

        # remove indentation
        if len(content) > 1:
            if content[0] == "":
                if self.get_flag(1)[0] != "u":
                    content[1] = content[1].lstrip()
            else:
                if self.get_flag(0)[0] != "u":
                    content[0] = content[0].lstrip()

        # remove spaces
        for k in range(len(content)):
            if self.get_flag(k)[0] == "u":
                content[k] = content[k].rstrip(self.strip_char)
            else:
                content[k] = content[k].strip(self.strip_char)
        return content

    def update_colwidth(self, content):
        thiscolwidth = [wclen(c) for c in content]
        for i, w in enumerate(thiscolwidth):
            if i < len(self.colwidth):
                self.colwidth[i] = max(self.colwidth[i], w)
            else:
                self.colwidth.append(w)

    def add_rows(self, row):
        content = self.get_cells(row)
        if len(content) <= 1:
            return False
        self.update_colwidth(content)
        self.rows.append(row)
        return True

    def detect_rows(self):
        view = self.view
        lastrow = view.rowcol(view.size())[0]

        for sel in view.sel():
            for line in view.lines(sel):
                thisrow = view.rowcol(line.begin())[0]
                if thisrow in self.rows:
                    continue
                if not self.add_rows(thisrow):
                    continue

            if sel.empty():
                thisrow = view.rowcol(sel.begin())[0]
                if thisrow not in self.rows:
                    continue
                beginrow = endrow = thisrow
                while endrow + 1 <= lastrow and not (endrow + 1 in self.rows):
                    if not self.add_rows(endrow + 1):
                        break
                    endrow = endrow + 1
                while beginrow - 1 >= 0 and not (beginrow - 1 in self.rows):
                    if not self.add_rows(beginrow - 1):
                        break
                    beginrow = beginrow - 1

    def fill_spaces(self, content):
        for k in range(len(content)):
            if self.colwidth[k] == 0:
                continue
            thisf = self.flag[k % len(self.flag)]
            align = thisf[0]
            if k == len(content) - 1 or self.get_flag(k + 1)[0] == 'u':
                pedding = ""
            else:
                pedding = " " * thisf[1]
            fill = self.colwidth[k] - wclen(content[k])
            if align == 'l' or align == 'u':
                content[k] = content[k] + " " * fill + pedding
            elif align == 'r':
                content[k] = " " * fill + content[k] + pedding
            elif align == 'c':
                lfill = " " * int(fill / 2)
                rfill = " " * (fill - int(fill / 2))
                content[k] = lfill + content[k] + rfill + pedding

    def get_span(self, row):
        # it is used to reset cursors in table mode
        line = self.get_line(row)
        p = [m.span() for m in re.finditer(self.regex, line)]
        if self.f > 0:
            p = p[0:self.f]
        p.append((len(line), None))
        cell = [(0, p[0][0])]
        for i in range(len(p) - 1):
            cell.append(p[i])
            cell.append((p[i][1], p[i + 1][0]))
        trimcell = []
        s = 0
        for i, c in enumerate(cell):
            cellcontent = line[c[0]:c[1]]
            b = s + wclen(cellcontent.rstrip(self.strip_char))
            a = b - wclen(cellcontent.strip(self.strip_char))
            trimcell.append((a, b))
            s = s + wclen(cellcontent)
        return trimcell

    def adjacent_lines_match(self):
        # it is used to check whether table mode should be disabled
        view = self.view
        lastrow = view.rowcol(view.size())[0]
        rows = []
        for sel in view.sel():
            for line in view.lines(sel):
                rows.append(view.rowcol(line.begin())[0])
        rows = list(set(rows))
        for row in rows:
            if len(self.get_cells(row)) > 1:
                continue
            elif row - 1 >= 0 and len(self.get_cells(row - 1)) > 1:
                continue
            elif row + 1 <= lastrow and len(self.get_cells(row + 1)) > 1:
                continue
            else:
                return False
        return True

    def reset_cursors(self, row, old_span, cursor):
        view = self.view
        # reset cursors' location
        new_span = self.get_span(row)
        if len(new_span) != len(old_span):
            return
        for s in view.sel():
            if s.empty and view.rowcol(s.end())[0] == row:
                view.sel().subtract(s)
        for cur in cursor:
            for i, c in reversed(list(enumerate(old_span))):
                newcur = 0
                if c[0] < cur:
                    if cur <= c[1]:
                        newcur = cur - c[0] + new_span[i][0]
                    else:
                        newcur = new_span[i][1] + self.get_flag(len(old_span) - i)[1]
                    break
            endcol = view.rowcol(view.line(view.text_point(row, 0)).end())[1]
            pt = view.text_point(row, min(newcur, endcol))
            view.sel().add(sublime.Region(pt, pt))

    def replace(self, edit):
        view = self.view

        if self.flag[0][0] != "u":
            indentation = min([re.match(r"^(\s*)",
                              self.get_line(row)).group(1) for row in self.rows])
        else:
            indentation = ""
        cursor_rows = set([view.rowcol(s.end())[0] for s in view.sel() if s.empty])

        for row in reversed(self.rows):
            if row in cursor_rows:
                # if this row contains cursors, record their locations
                span = self.get_span(row)
                cursor = [view.rowcol(s.end())[1] for s in view.sel()
                          if s.empty and view.rowcol(s.end())[0] == row]

            content = self.get_cells(row)
            self.fill_spaces(content)
            line = view.line(view.text_point(row, 0))
            view.replace(edit, line, (indentation + "".join(content).rstrip(self.strip_char)))

            if row in cursor_rows:
                self.reset_cursors(row, span, cursor)

    def run(self, edit):
        # check if regex is valid
        try:
            re.compile(self.regex)
        except Exception:
            return False

        self.detect_rows()

        if self.mode:
            for row in get_table_rows(self.view):
                self.add_rows(row)

        self.rows = sorted(set(self.rows))

        if not self.rows:
            return False

        if self.mode:
            set_table_rows(self.view, self.rows)

        self.replace(edit)
        return True
