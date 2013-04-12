Align Tabular
==============
This is a version of the excellent VIM plugin - tabular.

How does it differ from other alignment plugins?
------------
- Flexibility: Align with user defined regular expression
- Efficiency: Smart line detection for alignment if no lines are selected
- Multiple cursors support
- It is now working on both ST 2 and 3.

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

Examples
------------
###First Example
```
apple =   1==0
banana =100
 car = 2
```

- `=/f` or `=/lf` or `=/l1f` or `=/lf1` or `=/l1f1` gives (align only the first `=`)

```
apple  = 1==0
banana = 100
car    = 2
```

- `(?<==)\s*./l1r0l0f1` gives (align the first non-space character just after `=`)

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


- `&` or `&/l` or `&/l1` gives

```
apple & orange & grapes
one   & two    & three
```

- `&/c` gives (center aligned)

```
apple & orange & grapes
 one  &  two   & three
```

- `&/c0` gives (no space after columns)

```
apple&orange&grapes
 one & two  &three
```

- `&/c2l1` or `&/c2l` gives (two spaces after odd columns)

```
apple  & orange  & grapes
 one   &  two    & three
```

- `&/llclr` gives (each column has its own alignment)

```
apple & orange & grapes
one   &  two   &  three
```


Saved patterns
------------
To make it easier to remember complex patterns, you can save named patterns in
a dictionary in the settings file. Use the name as key and the alignment
expression as value. These patterns are included in the default file:

```
  "named_patterns": {
    "first_comma": "(?<=,)\\s*./l1r0l0f1",
    "first_colon": "(?<=:)\\s*./l1r0l0f1"
  }
```

You then just use the name instead of the pattern in the input field.

Keymaps
------------
If you often use a particular regex to align, you can put something like
this in your user keybind file.

```
  // latex align key bind
  {
    "keys": ["super+shift+a"], "command": "align_tab",
    "args" : {"user_input" : "&|\\\\\\\\"},
    "context":   [ { "key": "selector", "operator": "equal", "operand": "text.tex.latex" } ]
  }
```
