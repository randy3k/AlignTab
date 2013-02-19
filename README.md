Align Tabular
==============
This is a version of the excellent VIM plugin - tabular.

How does it differ from other alignment plugins?
------------
- Flexibility: Align with user defined regular expression
- Efficiency: Smart line detection for alignment if no lines are selected
- Multiple cursors support

Usage
------------
- Type `Align Tabular` in command palette.
- Enter delimiter in Python regex in the input panel
- The input format should be in the from of `regex/((?:[rlc][0-9]*)+)?(?:(f[0-9]*))?`
- The option `/((?:[rlc][0-9]*)+)?(?:(f[0-9]*))?` controls
 - left/right/center alignment
 - spaces after the columns
 - max number of splits
- Default option is `l1f0`. <br>
It means all columns are left-aligned. A space is added for each column. All matched delimiters are used.
- The option for alignment cycles through the columns. Note that delimiter is also a column.

Examples
------------
###First Example
```
apple = 1==0
banana = 0
car = 2
```
- `=/f` or `=/lf` or `=/l1f` or `=/lf1` or `=/l1f1` gives (align only the first `=`)

```
apple  = 1==0
banana = 0
car    = 2
```

- `(?<==)\s/l0l1` gives (aligning space)

```
apple =  1==0
banana = 0
car =    2
```


###Another Example
```
apple& orange & grapes
   red   & orange color & purple color
```


- `&` or `&/l` or `&/l1` gives

```
apple & orange       & grapes
red   & orange color & purple color
```

- `&/c` gives (center aligned)

```
apple &    orange    &    grapes
 red  & orange color & purple color
```
- `&/c0` gives (no space after columns)

```
apple&   orange   &   grapes
 red &orange color&purple color
```
- `&/c0l1` or `&/c0l` gives (no space after odd columns)

```
apple&    orange   &    grapes
 red & orange color& purple color
```
- `&/l0l2c0l2r0l2` gives (each column has its own alignment)

```
apple&     orange   &        grapes
red  &  orange color&  purple color
```

- `&/f` or `&/f1` gives (align only the first `&`)

```
apple & orange & grapes
red   & orange color & purple color
```


Saved patterns
------------
To make it easier to remember complex patterns, you can save named patterns in
a dictionary in the settings file. Use the name as key and the alignment
expression as value. These patterns are included in the default file:

```
  "named_patterns": {
    "first_comma": "(?<=,)\\s/l0l1f1",
    "first_colon": "(?<=:)\\s/l0l1f1"
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
