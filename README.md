platform: mac OS X

python version: Python 3.7

use --encode option and redirect std output to a file, then use a SAT solver to generate a inst-<instance num>.sat file. Use --decode option to decode .sat file.

```bash
usage: wiring.py [-h] [--encode] [--decode]
                 [--instance {inst-1.txt,inst-2.txt,inst-3.txt}]
                 [--solution {inst-1.sat,inst-2.sat,inst-3.sat}]

wiring problem

optional arguments:
  -h, --help            show this help message and exit
  --encode, -e          encode problem
  --decode, -d          decode problem
  --instance {inst-1.txt,inst-2.txt,inst-3.txt}, -i {inst-1.txt,inst-2.txt,inst-3.txt}
                        choose a instance to solve
  --solution {inst-1.sat,inst-2.sat,inst-3.sat}, -s {inst-1.sat,inst-2.sat,inst-3.sat}
                        choose a solution to decode
```
