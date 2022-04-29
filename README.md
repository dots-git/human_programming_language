## human programming language
a programming language aimed at being very true to natural language. it accomplishes that by means of using pattern matching.

## installation
you cannot yet install human. i am planning on releasing it on pipy.

## usage

```
# this is a basic example of the human
# programming language. 
# this particular line is a comment.


f of some x means:

    # number literals can be written in
    # digits (3, 91, etc) or in words
    # (three, ninety one, etc)

    Add up x and one

    # "result" is a variable that is always
    # the result of the last expression.
    # expressions like "print" return their
    # input value.

    Multiply the result by 3
    Subtract the result from two

g of some x means:

    # you can use functions in other functions,
    # even if they are defined later (example here: negative x)

    Multiply negative x by three
    Subtract one from the result

negative some number means:
    Subtract the number from zero

minus some number means:
    Subtract the number from zero

print out f of two
print out f of three
print out f of four


print out g of two
print out g of three
print out g of four

# statements in single or double quotes 
# will not be evaluated

print 'g of five'
print "g of six"

# to print single or double quotes, surround them 
# with the other quote type

print '"'
print "'"
```