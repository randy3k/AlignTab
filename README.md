AlignTab
==============
An alignment plugin for Sublime Text 2/3 -- ST version of the excellent VIM plugin, tabular.<br>
Note: ST2 support is deprecated and moved to [st2 branch](https://github.com/randy3k/AlignTab/tree/st2). You are still able to install AlignTab via Package Control, but no update (unless serious bug) will be provided.

Features
------------
- Align with user defined regular expression
- Custom spacing, padding and justification.
- Smart detection for alignment if no lines are selected
- Multiple cursors support
- Table mode: super efficient for editing tables

Usage
------------
###First time user

- Predefined alignment tools can be found under the mouse menu `Align By`

<img width=500 src="https://github.com/randy3k/AlignTab/raw/fig/alignby.png">

###Advanced user

- Open `AlignTab` in Command Palette `C+Shift+p`
- The input should be in the from of `regex/option`
- The option, e.g., `c2r2f1`, controls
 - column justification: `r`, `l` or `c`
 - spaces after each column: the number after `r`, `l` or `c`
 - max number of delimiters: the number after `f`
- Delimiter is also treated as a column.<br>
For example, `=/rcl` means the the column before `=` will be right-justifed and the column after `=` will be left-justified. And `=` will be centered (however, it doesn't matter as `=` is of length 1).
- The option for alignment cycles through the columns. <br>
For example, `regex/rl` means all odd columns will be right-justified and all even columns will be left-justified.
- the symbol `*` repeats the preceeding justification flags. 
<br>For example `r*3` equals `rrr`, and `(cr3)*2` equals `cr3cr3`.
- Default option is `l1f0`.
 * All columns are left-justified.
 * A space is added after each column.
 * All matched delimiters are aligned.
- Do not use capturing parenthese for regular expression. Instead, use non-capturing parenthese `(?:regex)`.

<img width=500 src="https://github.com/randy3k/AlignTab/raw/fig/aligntab.gif">

###Table Mode

<img width=500 src="https://github.com/randy3k/AlignTab/raw/fig/table.gif">


Installation
------------
[Package Control](http://wbond.net/sublime_packages/package_control)


[Examples](https://github.com/randy3k/AlignTab/wiki/Examples)
-----------

Keybinds
------------
For frequent patterns, put the following keybind in your user keybinds file. (Remember to change the key and regex.)

```
 //align =
  {
    "keys": ["super+shift+a"], "command": "align_tab",
    "args" : {"user_input" : "=/f"}
  }
```
or syntex specific keybind.

```
  // latex align keybind, to align & and \\, but not \&
    {
    	"keys": ["super+shift+a"], "command": "align_tab",
        "args" : {"user_input" : "(?<!\\\\)&|\\\\\\\\"},
        "context":[
            { "key": "selector", "operator": "equal", "operand": "text.tex.latex" }
        ]
    }
```



Named patterns
------------
To make it easier to remember complex patterns, you can save them in
a dictionary in the settings file. Use the name as key and the regex as value.
These patterns are included in the default file:

```
  "named_patterns": {
     "first_equal": "=/f",
     "first_comma": ",/f",
     "first_colon": ":/f"
  }
```

You then just use the name instead of the pattern in the input field.
To edit the patterns, go to `Perferences -> Package Settings -> AlignTab -> Settings`.
