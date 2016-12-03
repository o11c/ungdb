import re


class Tokenizer:
    def __init__(self, patterns):
        patterns = list(patterns)
        patterns.append(('ERROR', r'.', None))
        self._functions = {name: fun for (name, regex, fun) in patterns}
        assert len(self._functions) == len(patterns), 'Duplicate keys!'
        pattern = '|'.join('(?P<%s>%s)' % (name, regex) for (name, regex, fun) in patterns)
        self._pattern = re.compile(pattern)
        for (name, regex, fun) in patterns:
            setattr(self, name, name)

    def tokenize(self, input):
        for match in self._pattern.finditer(input):
            kind = match.lastgroup
            value = match.group(kind)
            assert value == match.group()
            if kind == self.ERROR:
                raise ValueError('input=%r, match=%r' % (input, match))
            else:
                fun = self._functions[kind]
                yield kind, fun(value)
