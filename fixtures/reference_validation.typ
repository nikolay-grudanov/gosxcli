// Test fixture for reference validation
// This file tests bidirectional validation of labels and references

= Introduction

This document tests reference validation.

= Defined Labels

The following sections, figures, tables, and equations are defined:

// Figure with label
#figure(
  image("diagram.png"),
  caption: [Experimental results],
) <fig:results>

// Table with label
#table(
  columns: 2,
  table.header([Parameter][Value]),
  [Temperature][298 K],
  [Pressure][1 atm],
) <tbl:data>

// Equation with label
$ E = mc^2 $ <eq:formula>

= References to Defined Labels

Now we reference all the defined labels:

- As shown in @fig:results, the experiment was successful.
- The data is presented in @tbl:data.
- The equation @eq:formula describes the relationship.

= Undefined Reference

This section contains a reference to a non-existent label:

// This reference is intentionally undefined
See @fig:missing for additional details.

= Unreferenced Label

This section defines a label that is never referenced:

// This label is intentionally unreferenced
#figure(
  image("unused.png"),
  caption: [This figure is never referenced],
) <label:unused>

= Conclusion

Reference validation test complete.
