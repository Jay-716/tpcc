.PHONY: all test

all: test

test: lexer_test parser_test quaternizer_test

lexer_test: test/lexer.test
	python3 main.py -l test/lexer.test

parser_test: test/parser.test
	python3 main.py -p test/parser.test

quaternizer_test: test/quaternizer.1.test test/quaternizer.2.test
	python3 main.py test/quaternizer.{1,2}.test
