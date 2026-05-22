# Grammer
## Types
- `$STR`: string
    ```
    "hello", "hello123", "hello world", "123", "!@#$#%##$@123df"
    ```
    Can contain alphabets, numbers, spesial characters inside double quots (`""`).

- `$INT`: integer
    ```
    123, 1000, 1343747
    ```
    Can contain only numbers.

- `$BOOL`: boolean
    ```
    TRUE, FALSE
   ```
   Only those two options.
- `$FLOAT`: float
    ```
    1.234, 0.122323, 3.1415, 1.0000
    ```
    Can contain only numbers with decimal point, can not start with `0`.

- `$BIN`: binary
    ```
    0b101010001, 0b1111111, 0b000101101, 0b000000
    ```
    Can contain only `0` and `1`, starting with `0b`.

- `$HEX`: hexadecimal
    ```
    0x123, 0xAAA, 0x12AA, 0xABCDEF, 
    ```
    Can contain only `0 - 0` and `A - F` starting with `0x`.

- `$OCT`: octal
    ```
    0o123, 0o1234, 0o4644612
    ```
    Can contain only `0 - 7` starting with `0o`.

- `$CHAR`: character
    ```
    'a', '1', '%'
    ```
    Can contain only one character of alphabets, numbers, spesial characters inside single quots (`''`).

## syntax
1. Each line must end with a space and a  semi colon ( ` ;` ).
2. The start of the bolck thet is to be executed must start with `START` statement.
3. Every script must end with a `END` statement.
4. If the execution of a code have to be ended in between, the `END` statement.
5. Variable name can only contain alphabet (*a-z, A-Z*), number (*0-9*) and a under score (*_*), can't start with a number.

## operators
### Arithmetic operators
| operator | meaning |
| -------- | ------- |
| `+` | addition |
| `-` | subtraction |
| `*` | multiplication |
| `/` | division |
| `%` | modulus |

### Comparison operators
| operator | meaning |
| -------- | ------- |
| `==` | equal to |
| `!=` | not equal to |
| `>` | greater than |
| `<` | less than |
| `>=` | greater than or equal to |
| `<=` | less than or equal to |

### Logical operators
| operator | meaning |
| -------- | ------- |
| `&&` | and |
| `\|\|` | or |
| `!` | not |

### bitwise operators
| operator | meaning |
| -------- | ------- |
| `&` | bitwise and |
| `\|` | bitwise or |
| `^` | bitwise xor |
| `~` | bitwise not |
| `<<` | left shift |
| `>>` | right shift |

### Special/Miscellaneous Operators
| operator | meaning |
| -------- | ------- |
| `=` | assignment |
| `&` | address of |
| `*` | dereference |
| `.` | dot |
| `->` | arrow |
| `,` | comma |
| `sizeof` | size of data |

## Keywords
1. `SET` - To assign value to a variable.
    ```
    # syntax:
    SET <variable_name> $<type> = <value> ;

    # example:
    SET name $STRING = "Bob" ;
    SET age $INT = 20 ;
    SET is_boy $BOOL = TRUE ;
    SET mark_percent $FLOAT = 75.89 ;
    SET grade $CHAR = 'B' ;
    ```

2. `PRINT` - To print a value to the terminal.
    ```
    # syntax:
    PRINT <value-1>, <value-2>, <value-3>, <value-n>, ... ;

    # example
    PRINT "BOB" ;
    PRINT 123 ;
    PRINT "mark: ", 90.5 ;
    ```

3. `INPUT` - To take input from the user.
    ```
    # syntax:
    INPUT <variable_name> $<type> ;

    # example:
    INPUT name $STRING ;
    INPUT age $INT ;
    INPUT is_boy $BOOL ;
    INPUT mark_percent $FLOAT ;
    INPUT grade $CHAR ;
    ```

4. `GOTO` - To jump to a label.
    ```
    # syntax:
    <lable_name>: <statement> ;
    ...
    GOTO <lable_name> ;
    ```
   
5. `IF-THEN-ELSE` - To check a condition.
    ```
    # syntax:
    # method 1
    IF <condition> THEN <statement> ELSE <statement> ;
    # method 2
    IF <condition> THEN 
        <statement-1> ;
        <statement-2> ;
        ...
        <statement-n> ;
    ELSE 
        <statement-1> ;
        <statement-2> ;
        ...
        <statement-n> ;
    ENDIF ;
    ```

6. `FOR-NEXT` - To iterate over a range.
   ```
    # syntax:
    # method 1: with out `STEP`
    FOR <control_variable> = <value> TO <end_value>
        <statement-1> ;
        <statement-2> ;
        ...
        <statement-n> ;
    NEXT <control_variable> ;
    
    # method 2: with `STEP`
    FOR <control_variable> = <value> TO <end_value> STEP <step_value>
        <statement-1> ;
        <statement-2> ;
        ...
        <statement-n> ;
    NEXT <control_variable> ;
   ```