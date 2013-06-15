Align Tabular
==============
An alignment plugin for Sublime Text 2/3 -- ST version of the excellent VIM plugin, tabular.

How does it differ from other alignment plugins?
------------
- Flexibility: Align with user defined regular expression
- Efficiency: Smart line detection for alignment if no lines are selected
- Multiple cursors support

Usage
------------
First time user

- Predefined alignment tools can be found under the top menu `Selection -> Align By`<br>
 or mouse menu `Align by`

<img src="https://github.com/randy3k/AlignTab/raw/master/alignby.png">

Advanced user

- Toogle Align Tabular, go the menu `Selection -> Align Tabular` or type `Align Tabular` in command palette.
- Enter delimiter in Python regex in the input panel
- The input should be in the from of `regex/((?:[rlc][0-9]*)+)?(?:(f[0-9]*))?`
- The option `/((?:[rlc][0-9]*)+)?(?:(f[0-9]*))?` controls
 - left/right/center justification: `r` or `l` or `c`
 - spaces after the columns: the number after `rlc`
 - max number of splits: the number after `f`
- Default option is `l1f0`. <br>
It means all columns are left-justified. A space is added after each column. All matched delimiters are aligned.
- The option for alignment cycles through the columns and delimiters are also columns.


Installation
------------
[Package Control](http://wbond.net/sublime_packages/package_control)


Examples
------------
###First Example
```
apple =   1==0
banana =100
 car = 2
```

- `=/f` or `=/lf` or `=/l1f` or `=/lf1` or `=/l1f1` aligns only the first `=`

```
apple  = 1==0
banana = 100
car    = 2
```

- `(?<==)\s*./l1r0l0f1` aligns the first non-space character just after `=`

```
apple =  1==0
banana = 100
car =    2
```


###Another Example
```
apple& orange &grapes
   one & two& three
```

- `&` or `&/l` or `&/l1` yields

```
apple & orange & grapes
one   & two    & three
```

- `&/c2l1` or `&/c2l` two spaces after odd columns

```
apple  & orange  & grapes
 one   &  two    & three
```

- `&/llclr` each column has its own justifications

```
apple & orange & grapes
one   &  two   &  three
```

Keybinds
------------
For frequent patterns, consider the following keybind in your user keybinds file. (Remember to change the key and regex.)

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
    "context":   [ { "key": "selector", "operator": "equal", "operand": "text.tex.latex" } ]
  }
```



Predefined patterns
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
To edit the patterns, go to `Perferences -> Package Settings -> Aligh Tabular -> Settings`.
