
# Copy+paste into terminal
import re
#re.regex('test')
regex=r'test'
match=re.search(regex, 'String under test')
[print(d) for d in dir(regex)]
[print(d) for d in dir(match)]
[print(d) for d in dir(match.re)]
#match.re.pattern
match.re.fullmatch
match.group(0)
