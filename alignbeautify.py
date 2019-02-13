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

####################################################
# This class applies Aligner to all of the buffer
# 'blocks'
# 'block' - is a part of buffer rows separated from
# others with empty rows
# After work - returning into first selection
####################################################

class AlignBeautifyCommand(sublime_plugin.TextCommand):
  def run(self, edit, user_input, block_no_align_rows = 0):
    view = self.view
    sel = view.sel()
    orig_sel = sel[0]

    # Get all of lines regions
    last_point = view.size()
    buffer_region = sublime.Region(0, last_point)
    lines = view.lines(buffer_region)

    # Translate lines regions into empty lines rows - separators of the blocks
    empty_rows = [-1] # First element is before file starts
    for line in lines:
      if (line.empty()):
        line_begin = line.begin()
        empty_row = view.rowcol(line_begin)[0]
        empty_rows.append(empty_row)

    # Append after file ends
    last_line_begin = lines[-1].begin()
    last_line_row = view.rowcol(last_line_begin)[0]
    empty_rows.append(last_line_row + 1)
    
    sublime.status_message("Rows: " + ', '.join(str(x) for x in empty_rows))

    # Iterate in rows from start until the end
    for i in range(0, len(empty_rows)-1):
      block_first_row = empty_rows[i] + 1
      block_last_row = empty_rows[i+1] - 1

      # Calculating block region 
      block_begin = view.text_point(block_first_row + int(block_no_align_rows), 0)
      block_end = view.line(view.text_point(block_last_row, 0)).end()
      block_region = sublime.Region(block_begin, block_end)
      
      # Selecting block
      sel.clear()
      sel.add(block_region)
        
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

      # Return selection to a place
      sel.clear()
      sel.add(orig_sel)
