import sublime
import sublime_plugin
from .aligner import Aligner

# Got it from align.py - Put it into class in future!
def resolve_input(user_input):
  if isinstance(user_input, str):
    s = sublime.load_settings('AlignTab.sublime-settings')
    patterns = s.get('named_patterns', {})
    if user_input == 'last_regex' and history.last():
      user_input = history.last()
    if user_input in patterns:
      user_input = patterns[user_input]
  if isinstance(user_input, str):
    user_input = [user_input]
  return user_input

########################################################
# This class applies Aligner to all of the buffer lines
########################################################

class AlignBeautifyCommand(sublime_plugin.TextCommand):
  def run(self, edit, user_input, block_no_align_rows = 0):
    view = self.view
    sel = view.sel()
    orig_sel = None
    
    # Trying to find current selection
    try:
      orig_sel = sel[0]
      orig_sel_begin = orig_sel.begin()
      orig_sel_x, orig_sel_y = view.rowcol(orig_sel_begin)

    except IndexError:
      sublime.status_message("There was no selection")

    finally:
      # Get all of lines regions
      last_point = view.size()
      buffer_region = sublime.Region(0, last_point)
      lines = view.lines(buffer_region)

      # Computing all the rows
      rows = []
      for line in lines:
        line_begin = line.begin()
        row = view.rowcol(line_begin)[0]
        rows.append(row)

      # Iterate in rows
      for row in rows:
        # Calculating block region 
        linepoint = view.text_point(row, 0)
        
        # Selecting block
        sel.clear()
        sel.add(linepoint)
          
        # Let the AlignTab do it`s work
        user_input = resolve_input(user_input)
        error = []
        for uinput in user_input:
          # apply align_tab
          aligner = Aligner(view, uinput, mode = False)
          self.aligned = aligner.run(edit)

          if self.aligned:
            sublime.status_message("")
          else:
            error.append(uinput)
        
        if error:
          errors = '    '.join(error)
          sublime.status_message("[Patterns not Found:   " + errors + "   ]")

        sel.clear()
        # Return selection to a place
        if (orig_sel):
          orig_sel = view.text_point(orig_sel_x, orig_sel_y)
          sel.add(orig_sel)
