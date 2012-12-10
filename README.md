Align Tabular
==============
This plug-in is an attempt to reproduce vim tabular functionality in sublimetext

Introduction
------------
- align selection with regular expression
- smart auto selection detection if no lines are selected
- multiple selection support

Usage
------------
- Type `Align Tabular` in command palette.
- Enter delimiter in Python regex in the input panel
- The input format should be in the from of `regex/((?:[rlc][0-9]*)+)?(?:(f[0-9]*))?`
- The option `/((?:[rlc][0-9]*)+)?(?:(f[0-9]*))?` controls
 - left/right/center alignment
 - spaces after the columns
 - max number of splits
- Default option is `l1`. <br>
It means all columns are left-aligned. A space is added for each column. All matched delimiters are used.
- The option for alignment cycles through the columns. Note that delimiter is also a column.

Examples
------------
###First toy
```
apple& orange & grapes
   red   & orange color & purple color
```


- `&` gives

```
apple & orange       & grapes
red   & orange color & purple color
```

- `&/c` gives

```
apple &    orange    &    grapes
 red  & orange color & purple color
```
- `&/c0` gives

```
apple&   orange   &   grapes
 red &orange color&purple color
```
- `&/c0l1` or `&/c0l` gives

```
apple&    orange   &    grapes
 red & orange color& purple color
```
- `&/l0l2c0l2r0l2` gives

```
apple&     orange   &        grapes
red  &  orange color&  purple color
```

###Another toy (only the first delimiter is detected):

```
apple = banana==1
banana = car==0
car = dog
```
- `=/f` or `=/lf` or `=/l1f` or `=/lf1` or `=/l1f1` aligns  to

```
apple  = banana==1
banana = car==0
car    = dog
```

Keymaps
------------
If you use a same regex to align frequently, you can put something similar below in to your user keyblind file.

```
  // latex align key blind
  {
    "keys": ["super+shift+a"], "command": "align_tab",
    "args" : {"user_input" : "&|\\\\\\\\"},
    "context":   [ { "key": "selector", "operator": "equal", "operand": "text.tex.latex" } ]
  }
```