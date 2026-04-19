#import "@preview/modern-g7-32:0.2.0": *

#show: modern-g7-32.with(
  title: [Code Blocks Test],
  author: [Test Author],
)

= Introduction

Here is a Python code block:

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Example usage
result = fibonacci(10)
print(f"F(10) = {result}")
```

And a code block without language:

```
This is plain text code.
```

= Conclusion
