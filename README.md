Align Tabular
==============
This plug-in is an attempt to reproduce vim tabular functionality in sublimetext

Introduction
------------
- align selection with regular expression
- auto selection detection if no lines are selected
- multiple selection support

Usage
------------
- Type `Align Tabular` in command palette.
- Enter delimiter in Python regex in the input panel
- The input format should be in the from of `regex/([lcr][0-9]*)+`
- The option `([lcr][0-9]*)+` contols the left/right/center alignment and the spaces after the columns.<br>
Default option is `l1`. The option cycles through the columns.

Examples
------------
There are some demo on how to align
```
apple& orange & grapes
   red   & orange color & purple color
```


- `&` aligns to

```
apple & orange       & grapes
red   & orange color & purple color
```

- `&/c` aligns to

```
apple &    orange    &    grapes
 red  & orange color & purple color
```
- `&/c0` aligns to

```
apple&   orange   &   grapes
 red &orange color&purple color
```
- `&/c0l1` aligns to

```
apple&    orange   &    grapes
 red & orange color& purple color
```
- `&/l0l2c0l2r0l2` aligns to

```
apple&     orange   &        grapes
red  &  orange color&  purple color
```

Keymaps
------------
If you always use the same regex to align, you can put the following in your user keyblind file.

```
  // latex align key blind
  {
    "keys": ["super+shift+a"], "command": "align_tab",
    "args" : {"user_input" : "&|\\\\\\\\"}
  }
```