#!/usr/bin/python
# Input:
#  TSV file to display
#  AWK expression for the resulting line, e.g. '{print $1;}'
#  Optional: default value
# On success:
#   runs the awk expression on the selected line
#   exit 0
# On control-C:
#   exit 1
# On failure:
#   error message to stderr
#   silence on stdout
#   exit 2

# Input file format:
# Lines beginning with # are headers
# Lines without # are numbered and shown to the user
# The user can enter a number, or a value from any of the columns to choose
# the line.  Ambiguous entries are retried.

import sys

def PickLine(filename, awk_expression='{print}', prompt="Choose one",
             default_answer=None, split_param='\t'):
  data = Data(filename, split_param)
  data.Load()
  data.PrintSelf(sys.stderr)
  if default_answer:
    _prompt = "%s [%s]: " % (prompt, default_answer)
  else:
    _prompt = "%s: " % prompt

  try:    
    while True:
      print >> sys.stderr, _prompt,
      # input = sys.stdin.read().rstrip()
      input = raw_input()
      if not input:
        input = default_answer
      try:
        result = data.Matches(input)
        break
      except Empty:
        pass
      except Ambiguous:
        print >> sys.stderr, "Answer is ambiguous. Try again."
      except NoMatch:
        print >> sys.stderr, "Answer not recognized. Try again."
    # TODO: now run awk on `result
    print result
  except KeyboardInterrupt:
    return None
  except EOFError:
    return None
    
  
class Ambiguous(Exception):
  pass


class NoMatch(Exception):
  pass
  
  
class Empty(Exception):
  pass


class Data(object):
  """Represents a whole input file"""
  def __init__(self, filename, split_param='\t'):
    super(Data, self).__init__()
    self.filename = filename
    self.saved_lines = []
    self.counted_lines = []
    self.split_param = split_param
    
  def Load(self):
    """docstring for Load"""
    f = open(self.filename, 'r')
    self._LoadFromIterable(f)
    
  def _LoadFromIterable(self, f):
    for line in f:
      if line: line = line[:-1] 
      if line and not line[0] == '#':
        self._CountLine(line)
      else:
        self._SaveLine(line[1:])
  
  def _CountLine(self, line):
    self.counted_lines.append(line)
    self._SaveLine(" %2d. %s" % (len(self.counted_lines), line))
  
  def _SaveLine(self, line):
    self.saved_lines.append(line)
  
  def PrintSelf(self, out):
    """docstring for PrintSelf"""
    for line in self.saved_lines:
      out.write('%s\n' % line)
      
  def Matches(self, input):
    """docstring for Matches"""
    if not input:
      raise Empty()
      
    found = []
    num = 0
    for line in self.counted_lines:
      num += 1
      if self._Match(line, num, input):
        found.append(line)
    if len(found) > 1:
      raise Ambiguous()
    elif len(found) == 0:
      raise NoMatch()
    else:
      return found[0]
      
  def _Match(self, line, num, input):
    if str(num) == input: return True
    parts = line.split(self.split_param)
    for part in parts:
      if input == part: return True
    return False
  
#data = Data("none")
#data._LoadFromIterable([
  #"#Header\n",
  #"\n", # blank line
  #"one\t/dev/one\n",
  #"two\t/dev/two\n",
  #"twe\t/dev/two\n",
#])

#data.PrintSelf(sys.stdout)
#print data.Matches('1')
#print data.Matches('one')
#print data.Matches('/dev/one')

def main():
  PickLine(sys.argv[1])

if __name__ == "__main__":
    main()
