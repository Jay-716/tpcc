# tpcc - Tiny PasCal Compiler

***

## Description
**tpcc** is a very very simple compiler(quaternion translator, actually) for a pascal-like language. Syntax demos can be found in the `test` directory.   
This compiler use very simple LL(1) recursive method to parse and translate.   
Yeah, this is my Compiler Principles homework. :) So just feel free to use or copy-paste it for **EDUCATIONAL** usage.   

***

## Requirements
 - python>=3.10   

***

## Usage
```
usage: main.py [-h] [-o OUTPUT] [-l] [-p] [-q] input_files [input_files ...]

tpcc - Tiny PasCal Compiler

positional arguments:
  input_files           Input file(s)

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file
  -l, --lexer           Run lexer only
  -p, --parser          Run lexer and parser only(override -l --lexer)
  -q, --quaternizer     Run lexer, parser, and quaternizer(default)
```   
Use ```make [test_type]``` to automatically run tests.   
```test_types: lexer_test, parser_test, quaternizer_test```

***

## Reference
 - Lexer: Taken from [mipl](https://github.com/duchenerc/mipl)
 - Operator-Precedence Parsing: Refer to [wikipedia](https://en.wikipedia.org/wiki/Operator-precedence_parser)

