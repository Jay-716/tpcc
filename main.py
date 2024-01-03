from argparse import ArgumentParser
import sys
from lexer import Lexer
from parser import Parser
from quaternizer import Quaternizer


arg_parser = ArgumentParser(description='tpcc - Tiny PasCal Compiler')
arg_parser.add_argument('-o', '--output', required=False, help='Output file')
arg_parser.add_argument('-l', '--lexer', action='store_true', required=False, help='Run lexer only')
arg_parser.add_argument('-p', '--parser', action='store_true', required=False, help='Run lexer and parser only(override -l --lexer)')
arg_parser.add_argument('-q', '--quaternizer', action='store_false', required=False, help='Run lexer, parser, and quaternizer(default)')
arg_parser.add_argument('input_files', nargs='+', help='Input file(s)')
args = arg_parser.parse_args()

if args.input_files is None:
    print('Fatal: no input files', file=sys.stderr)
    exit(1)

for input_file in args.input_files:
    run_lexer = args.lexer
    run_parser = args.parser
    run_quaternizer = args.quaternizer
    if run_lexer:
        tokens = list(Lexer(input_file).get_tokens())
        results = tokens
    elif run_parser:
        tokens = list(Lexer(input_file).get_tokens())
        nodes = Parser(tokens).parse()
        results = nodes
    else:
        tokens = list(Lexer(input_file).get_tokens())
        nodes = Parser(tokens).parse()
        quaternions = Quaternizer(nodes).generate()
        results = quaternions
    if args.output is not None:
        output_file = open(args.output, 'w+')
        i = 0
        for item in results:
            i += 1
            print(f'({i})', item, file=output_file)
    else:
        i = 0
        for item in results:
            i += 1
            print(f'({i})', item)
