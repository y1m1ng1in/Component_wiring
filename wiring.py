import argparse
import sys

class Predicate:

  def __init__(self, n_component):
    self.n_component = n_component
    self.left_max = self.n_component ** 2
    self.right_max = 1 + self.n_component ** 2 + self.left_max
    self.w_max = 1 + self.right_max + self.n_component ** 2
    self.c_max = 1 + self.w_max + self.n_component ** 2
    
  def __inrange(self, *args):
    for arg in args:
      if arg >= self.n_component or arg < 0:
        return False
    return True

  # component 0 .. n_component-1
  # position 0 .. n_component -1 
  def l(self, component, position):
    assert self.__inrange(component, position)
    lit = self.n_component * position + component + 1
    assert lit >= 1 and lit <= self.left_max
    return lit

  # component 0 .. n_component-1
  # position 0 .. n_component -1 
  def r(self, component, position):
    assert self.__inrange(component, position)
    lit = self.left_max + self.n_component * position + component + 1
    assert lit >= 1 + self.left_max and lit <= self.right_max
    return lit

  # left position 0 .. n_component-1
  # right position 0 .. n_component-1
  def w(self, l_pos, r_pos):
    assert self.__inrange(l_pos, r_pos)
    lit = self.right_max + self.n_component * l_pos + r_pos + 1
    assert lit >= 1 + self.right_max and lit <= self.w_max
    return lit

  # left component 0 .. n_component-1
  # right component 0 .. n_component-1
  def c(self, l_component, r_component):
    assert self.__inrange(l_component, r_component)
    lit = self.w_max + self.n_component * l_component + r_component + 1
    assert lit >= 1 + self.w_max and lit <= self.c_max
    return lit


class Cnf:

  def __init__(self, instance):
    self.instance = instance
    self.mat_connection = []
    self.n = -1
    self.__read_file()
    self.preds = Predicate(self.n)
    self.clauses = []

  def encode(self):
    assert self.clauses == []
    self.__singleton()
    self.__existence()
    self.__uniqueness()
    self.__connection()
    self.__no_crossing()
    print("p", "cnf", self.preds.c_max, len(self.clauses))
    for c in self.clauses:
      print(*c, 0)

  def __clause(self, *args):
    self.clauses.append(args)

  def __existence(self):
    for comp in range(self.n):
      # For all i . Exists j . l(i, j)
      self.__clause(*[self.preds.l(comp, pos) for pos in range(self.n)])
      # For all i . Exists j . r(i, j)
      self.__clause(*[self.preds.r(comp, pos) for pos in range(self.n)])

  def __uniqueness(self):
    for pos in range(self.n):
      for comp1 in range(self.n):
        for comp2 in range(comp1 + 1, self.n):
          # For all k . For all i, j | i =/= j . not l(i, k) or not l(j, k)
          self.__clause(-self.preds.l(comp1, pos), -self.preds.l(comp2, pos))
          # For all k . For all i, j | i =/= j . not r(i, k) or not r(j, k)
          self.__clause(-self.preds.r(comp1, pos), -self.preds.r(comp2, pos))
  
  def __connection(self):
    for comp1 in range(self.n):
      for comp2 in range(self.n):
        for pos1 in range(self.n):
          for pos2 in range(self.n):
            # For all h, i, j, k . not l(h, j) or not r(i, k) or not c(h, i) or w(j, k)
            self.__clause(-self.preds.l(comp1, pos1), -self.preds.r(comp2, pos2),
                          -self.preds.c(comp1, comp2), self.preds.w(pos1, pos2))
            # For all h, i, j, k . not l(h, j) or not r(i, k) or not w(j, k) or c(h, i)             
            self.__clause(-self.preds.l(comp1, pos1), -self.preds.r(comp2, pos2),
                          -self.preds.w(pos1, pos2), self.preds.c(comp1, comp2))
  
  def __no_crossing(self):
    """     |          |
          left1(k)  right2(j)
            |          |
          left2(i)  right1(m)
            |          |
    """
    for pos_left_1 in range(self.n):
      for pos_left_2 in range(pos_left_1 + 1, self.n):
        for pos_right_2 in range(self.n):
          for pos_right_1 in range(pos_right_2 + 1, self.n):
            # For all i, j, k, m | k < i and m > j . not w(i, j) or not w(k, m)
            self.__clause(-self.preds.w(pos_left_1, pos_right_1),
                          -self.preds.w(pos_left_2, pos_right_2))

  def __singleton(self):
    for i in range(self.n):
      for j in range(self.n):
        if self.mat_connection[i][j] == 0:
          self.__clause(-self.preds.c(i, j))
        elif self.mat_connection[i][j] == 1:
          self.__clause(self.preds.c(i, j))
        else:
          raise Exception("Connection matrix must be value of 0 or 1.")

  def __read_file(self):
    mat_connection = []
    with open(self.instance, 'r') as f:
      for line in f:
        mat_connection.append([0 if i == 'f' else 1 for i in line[:-1]])
      self.mat_connection = mat_connection
      self.n = len(self.mat_connection)
      f.close()
    assert self.n != 0
    

class Decoder:

  def __init__(self, preds, solution):
    self.lits = []
    self.preds = preds
    self.n = preds.n_component
    self.solution = solution
    self.__read_file()

  def decode(self, filename=None):
    assert self.lits
    result = []
    for pos in range(self.n):
      for comp in range(self.n):
        if self.preds.l(comp, pos) in self.lits:
          print('left', comp+1)
          result.append([comp+1])
    index = 0
    for pos in range(self.n):
      for comp in range(self.n):
        if self.preds.r(comp, pos) in self.lits:
          print('right', comp+1)
          result[index].append(comp+1)
          index += 1
    if filename:
      with open(filename, 'w') as f:
        for comps in result:
          f.write(str(comps[0]) + ' ' + str(comps[1]) + '\n')
        f.close()

  def __read_file(self):
    with open(self.solution, 'r') as f:
      l = f.readline()
      tmp = l.split()
      self.lits = [int(i) for i in tmp[1:]]
      f.close()


instances = [
  'inst-1.txt',
  'inst-2.txt',
  'inst-3.txt'
]

solns = [
  'inst-1.sat',
  'inst-2.sat',
  'inst-3.sat'
]

write_solns = [
  'soln-default.txt',
  'soln-1.txt',
  'soln-2.txt',
  'soln-3.txt'
]

parser = argparse.ArgumentParser(description="wiring problem")
parser.add_argument('--encode', '-e', action="store_true", help="encode problem")
parser.add_argument('--decode', '-d', action="store_true", help="decode problem")
parser.add_argument('--instance', 
                    '-i', 
                    type=str, 
                    choices=instances, 
                    default=instances[0],
                    help="choose a instance to solve")
parser.add_argument('--solution',
                    '-s',
                    type=str,
                    choices=solns,
                    default='soln-1.sat',
                    help="choose a solution to decode")
parser.add_argument('--write',
                    '-w',
                    type=str,
                    choices=write_solns,
                    default=write_solns[0],
                    help="write solutions to a file")

args = parser.parse_args()

if (args.encode and args.decode) or (not args.encode and not args.decode):
  print("Must choose --encode **OR** --decode")
  sys.exit()

if args.encode:
  c = Cnf(args.instance)
  c.encode()

elif args.decode:
  assert args.solution in solns
  if args.solution == solns[0]:
    p = Predicate(3)
  elif args.solution == solns[1]:
    p = Predicate(3)
  else: 
    p = Predicate(8)
  d = Decoder(p, args.solution)
  d.decode(filename=args.write)

else:
  raise Exception("unsupported args")