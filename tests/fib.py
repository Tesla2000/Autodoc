from __future__ import annotations


def fibonacci_doc(n: int) -> int:
    """
    Documentation
    :param n:
    :return:
    """
    if n <= 0:
        raise ValueError("The input must be a positive integer.")
    elif n == 1:
        return 0
    elif n == 2:
        return 1

    a, b = 0, 1
    for _ in range(2, n):
        a, b = b, a + b
    return b


def fibonacci(n, a: int = 0, b: int = 1) -> int:
    """
    This function calculates the nth Fibonacci number using a loop and two
    initial values, `a` and `b`, representing the first two numbers in the
    sequence. It raises a ValueError if the input is not a positive integer and
    returns the calculated Fibonacci number.
    :param n: `n` represents the desired position in the Fibonacci sequence.
    :param a: `a` represents the first value in the Fibonacci sequence used to
    calculate the nth Fibonacci number.
    :param b: `b` represents the second value in the Fibonacci sequence, used
    to calculate subsequent numbers.
    :return: This function calculates the nth Fibonacci number using a loop and
    two initial values.
    """
    if n <= 0:
        raise ValueError("The input must be a positive integer.")
    elif n == 1:
        return 0
    elif n == 2:
        return 1

    for _ in range(2, n):
        a, b = b, a + b
    return b
