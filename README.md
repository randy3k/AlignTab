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
- Type `Align Tabular` in command palette.
- Enter delimiter in Python regex in the input panel
- The input should be in the from of `regex/((?:[rlc][0-9]*)+)?(?:(f[0-9]*))?`
- The option `/((?:[rlc][0-9]*)+)?(?:(f[0-9]*))?` controls
 - left/right/center alignment: `r` or `l` or `c`
 - spaces after the columns: the number after `rlc`
 - max number of splits: the number after `f`
- Default option is `l1f0`. <br>
It means all columns are left-aligned. A space is added after each column. All matched delimiters are aligned.
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

- `&/c` aligns at center

```
apple & orange & grapes
 one  &  two   & three
```

- `&/c0` no space after columns

```
apple&orange&grapes
 one & two  &three
```

- `&/c2l1` or `&/c2l` two spaces after odd columns

```
apple  & orange  & grapes
 one   &  two    & three
```

- `&/llclr` each column has its own alignment

```
apple & orange & grapes
one   &  two   &  three
```


Saved patterns
------------
To make it easier to remember complex patterns, you can save named patterns in
a dictionary in the settings file. Use the name as key and the alignment
expression as value. 
These patterns are included in the default file:

```
  "named_patterns": {
    "first_comma": "(?<=,)\\s*./l1r0l0f1",
    "first_colon": "(?<=:)\\s*./l1r0l0f1"
  }
```

You then just use the name instead of the pattern in the input field.
To edit the patterns, go to Perferences -> Package Settings -> Aligh Tabular -> Settings.

Keymaps
------------
For frequent patterns, consider the following keybind in your User KeyBindings.

```
  // latex align key bind
  {
    "keys": ["super+shift+a"], "command": "align_tab",
    "args" : {"user_input" : "&|\\\\\\\\"},
    "context":   [ { "key": "selector", "operator": "equal", "operand": "text.tex.latex" } ]
  }
```
