AlignTab
==============
[![Build Status](https://travis-ci.org/randy3k/AlignTab.svg?branch=master)](https://travis-ci.org/randy3k/AlignTab)

The most flexible alignment plugin for Sublime Text 2/3<br>
This plugin is inspired by the excellent VIM plugin, tabular.

Note: ST2 support is deprecated and moved to [ST2](https://github.com/randy3k/AlignTab/tree/st2) branch. 
However, you are still able to install AlignTab to ST2 via Package Control.

Features
------------
- Align using regular expression
- Custom spacing, padding and justification.
- Smart detection for alignment if no lines are selected
- Multiple cursors support
- Table mode and Live preview mode

Usage
------------
### Getting start

- Predefined alignment

<img width=500 src="https://github.com/randy3k/AlignTab/raw/fig/alignby.png">

### Welcome to the regex world

- Open `AlignTab` in Command Palette `C+Shift+p` and enter `regex/option` in the input panel
- The option controls column justification, pedding and maxinum number of splits.
- For example: `c2r3f1`
  - first column is centered followed by 2 spaces
  - second coumn is right-flushed followed by 3 spaces
  - only the first delimiter is matched

#### More about regex and options

- Use non-capturing parenthese `(?:regex)` instread of capturing parenthese.
 
- Delimiter is also treated as a column.<br>
For example, `=/rcl` means the the column before `=` will be right-justifed and the column after `=` will be left-justified. And `=` will be centered (however, it doesn't matter as `=` is of length 1).
- The option for alignment cycles through the columns. <br>
For example, `regex/rl` means all odd columns will be right-justified and all even columns will be left-justified.
- the symbol `*` repeats the preceeding justification flags. 
<br>For example `r*3` equals `rrr`, and `(cr3)*2` equals `cr3cr3`.

- Default option is `l1f0`.
  - All columns are left-justified.
  - A space is added after each column.
  - All matched delimiters are aligned.



### Live Preview Mode

<img width=500 src="https://github.com/randy3k/AlignTab/raw/fig/aligntab.gif">

### Table Mode

<img width=500 src="https://github.com/randy3k/AlignTab/raw/fig/table.gif">


Installation
------------
[Package Control](http://wbond.net/sublime_packages/package_control)


Examples
------------
Some simple examples. You can also contribute your examples there.
[Examples](https://github.com/randy3k/AlignTab/wiki/Examples)

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
    "first_equal" : "=/f",
    "first_comma" : ",/f",
    "first_colon" : ":/f",
    "all_and"     : "&",
    "all_bar"     : "\\|",
    "all_space"   : "\\s*/l1l0"
  }
```

You then just use the name instead of the pattern in the input field.
To edit the patterns, go to `Perferences -> Package Settings -> AlignTab -> Settings`.

Custom Context Menu
----
To define new item in the context menu, go to `Perferences -> Package Settings -> AlignTab -> Context Menu` and add

```
[
   {"caption" : "-"},
    {
      "id": "aligntab",
      "caption": "Align By",
      "children": [
          {
          "caption" : "{",
          "command" : "align_tab",
          "args"    : {"user_input" : "\\{"}
          }
      ]
  }
]
```


CJK Support
---
AlignTab supoorts CJK characters, but you have to choose a correct font face and font size.
To my knowledge, `MinCho` works on all Chinese, Japanese and Korean.

<img width=300 src="https://github.com/randy3k/AlignTab/raw/fig/cjk.png">

### License

AlignTab is licensed under the MIT License.
