# AlignTab

[![Build Status](https://travis-ci.org/randy3k/AlignTab.svg?branch=master)](https://travis-ci.org/randy3k/AlignTab)
[![Build status](https://ci.appveyor.com/api/projects/status/cwgpoqu0yial03w5?svg=true)](https://ci.appveyor.com/project/randy3k/aligntab)
[![Coverage Status](https://coveralls.io/repos/github/randy3k/AlignTab/badge.svg?branch=master)](https://coveralls.io/github/randy3k/AlignTab?branch=master)
<a href="https://packagecontrol.io/packages/AlignTab"><img src="https://packagecontrol.herokuapp.com/downloads/AlignTab.svg"></a>
<a href="https://www.paypal.me/randy3k/5usd" title="Donate to this project using Paypal"><img src="https://img.shields.io/badge/paypal-donate-blue.svg" /></a>
<a href="https://gratipay.com/~randy3k/" title="Donate to this project using Gratipay"><img src="https://img.shields.io/badge/gratipay-donate-yellow.svg" /></a>

The most flexible alignment plugin for Sublime Text 3. This plugin is inspired by the excellent VIM plugin, [tabular](https://github.com/godlygeek/tabular).

ST2 support is deprecated but however, it is still possible to install AlignTab on ST2 via Package Control.


## Features
- Align using regular expression
- Custom spacing, padding and justification.
- Smart detection for alignment if no lines are selected
- Multiple cursors support
- Table mode and Live preview mode

## Getting started

- If you only want simple and quick alignment, the predefined alignment will help.

<img width=650 src="https://user-images.githubusercontent.com/1690993/30779107-029a5934-a0b5-11e7-8523-7a3bb657b8f2.png">

## More complicated usage

- Open `AlignTab` in Command Palette `C+Shift+p` and enter the input in the form of `<regex>/<option>`.
- To learn more about regular expression, visit [here](http://www.regular-expressions.info) and [here](https://docs.python.org/2/library/re.html).
- The option controls column justification, padding and maximum number of splits. A general syntax of options is `([rlc][0-9]*)*(f[0-9]*)?`.
- The numbers after `r`, `c` or `l` determine how many spaces will be added after columns and the number after `f` controls how many matches will be made based `<regex>`.
- For example, `c2r3f1` means
  - first column is centered followed by 2 spaces
  - second column is right-flushed followed by 3 spaces
  - only the first match is used
- If the number after `[rlc]` is omitted, 1 space will be added after each column.
- If the number after `f` is omitted, only the first match will be used.
- The entire option could be omitted (i.e., input only the regular expression). In that case, default option, `l1f0` will be used. It means:
  - All columns are left-justified.
  - A space is added after each column.
  - All matched delimiters are aligned.


## More about regex and options

- Use non-capturing parenthese `(?:regex)` instread of capturing parenthese.
- Delimiter is also treated as a column.
  - For example, `=/rcl` means the the column before `=` will be right-justifed and the column after `=` will be left-justified. And `=` will be centered (however, it doesn't matter as `=` is of length 1).
- The option for alignment cycles through the columns. <br>
  - For example, `regex/rl` means all odd columns will be right-justified and all even columns will be left-justified.
- The symbol `*` repeats the preceeding justification flags. 
  - For example `r*3` equals `rrr`, and `(cr3)*2` equals `cr3cr3`.
- (Experimental) Besides `r`, `c` and `l`, there is a new `u` flag which stands for "unjustified".

## Live Preview Mode

<img width=650 src="https://cloud.githubusercontent.com/assets/1690993/23576654/4d4fe048-0079-11e7-9fed-ece0850b1312.gif">

## Table Mode

<img width=650 src="https://cloud.githubusercontent.com/assets/1690993/23576656/567bacec-0079-11e7-86ce-deaab5907acb.gif">

Hit <kbd>ESC</kbd> or use the command `AlignTab: Exit Table Mode` to exit table mode.


## Installation

[Package Control](http://wbond.net/sublime_packages/package_control)


## Examples

Some simple examples. You can also contribute your examples [there](https://github.com/randy3k/AlignTab/wiki/Examples).

## Keybinds

If you are interested in getting a keybind for live preview mode, add the following in your user keybinds file.
```
 {
   "keys": ["super+shift+a"], "command": "align_tab",
   "args" : {"live_preview" : true}
 }
```


For frequent patterns, you can consider the following in your user keybinds file. Change the keybind and the `user_input` for your purpose.

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



## Named patterns

To make it easier to remember complex patterns, you can save them in a dictionary in the settings file. To edit the patterns, launch `Preferences: AlignTab Settings`. Use the name as key and the regex as value. For examples,

```
"named_patterns": {
    "eq" : "=/f",
    // right hand side could also be an array of inputs
    "ifthen" : ["=/f", "\\?/f", ":/f"]
}
```

You then just use the name instead of the pattern in the input field.

## Custom Context Menu

To define new item in the context menu, launch `Preferences: AlignTab Context Menu` and add, for example

```
[
   {"caption" : "-"},
    {
      "id": "aligntab",
      "caption": "AlignTab",
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


## CJK Support

AlignTab supoorts CJK characters, but you have to choose a correct font face and font size.
To my knowledge, `MinCho` works on all Chinese, Japanese and Korean.

<img width=300 src="https://cloud.githubusercontent.com/assets/1690993/23576648/13fb5020-0079-11e7-9ffa-a10d5443192d.png">

## License

AlignTab is licensed under the MIT License.
