
<img src="./fcl-logo-512x512.png" class="center"/>

# The FCL Programming Language 

**FCL** (function-centered-langauge) is a functional programming language that takes the concept of functional programming to the extreme. In FCL, functions are used for everything (although you still can't define functions yet!) - from basic arithmetic operations to control flow statements. The goal of FCL is to simplify programming by reducing code "complexity" and increasing code "reusability" through the use of functions.

**FCL** has a simple syntax with a minimal set of keywords, making it easy for beginners to learn. However, its reliance on functions makes it a powerful tool for experienced developers as well. FCL also supports dynamic typing, making it flexible for a wide range of use cases.

While **FCL** is not a serious project, it serves as an interesting experiment in extreme functional programming. Give it a try and see how functions can be used in unexpected ways! (idk if it's that extreme tho)

This description was generted using ChatGPT 💀, quotes added by me ;)

⚠️ Note: All Code blocks use python's syntax highlighting

## Variables

Variables can be defined the normal way `varname = value` or by using the `var` function

```py
# doing this is
name = "FCL" 
# is same as
var(ident, "value") 
```

## Loops

```py
for (i, 0, 10, (
    log("Hello this is from inside the for loop!"), # comma is optional
    log("Our Current iteration is", i)
    log("Ending the iteration.")
)) # for loop signature: for(identifier, integer, expression) we use () for multiline expression
```

## Condtion

```py
if (false,  
    log("it was true"),
    elif(false, log("it was false")),
    elif(true, (
        log("2nd elif triggered")
        log("with multiline")
    )),
    log("this is just else case")
) # if function: if(cond, elif.. (optional), else_expr)

# to compare values we use functions like eq, neq, gt, gte, lt, lte
log("5 is equal to 2", eq(5, 2))
log("5 is not equal to 2", neq(5, 2))
log("5 is greater than 2", gt(5, 2))
log("5 is less than 2", lt(5, 2))
log("5 is greater than and equal to 2", gte(5, 2))
log("5 is less than and equal to 2", lte(5, 2))
```

## FizzBuzz
```py
# FizzBuzz implementation in FCL
for (i, 1, 101, (
    if (
        and(eq(mod(i, 3), 0), eq(mod(i, 5), 0)), 
        log("FizzBuzz"),
        elif(eq(mod(i, 3), 0), log("Fizz")),
        elif(eq(mod(i, 5), 0), log("Buzz")),
        log(i)
    ),
))
```

### [examples](/examples/)


#### Socials
- [YouTube](https://www.youtube.com/@FlinCode)
- [Twitter](https://twitter.com/fus3_n)
- [Reddit](https://www.reddit.com/user/FUS3N)



<style>
.center {
  display: block;
  margin-left: auto;
  margin-right: auto;
  width: 30%;
}
</style>