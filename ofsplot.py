#!/usr/bin/env python
from __future__ import print_function

import inkex
import cubicsuperpath, simplestyle, copy, math, re, bezmisc, simplepath
import pyclipper
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)



class ofsplot(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("--count",
                        action="store", type="int",
                        dest="count", default=10,
                        help="Number of offset operations")
        self.OptionParser.add_option("--ofs",
                        action="store", type="float",
                        dest="offset", default=2,
                        help="Offset amount")
        self.OptionParser.add_option("--init_ofs",
                        action="store", type="float",
                        dest="init_offset", default=2,
                        help="Initial Offset Amount")
        self.OptionParser.add_option("--copy_org",
                        action="store", type="inkbool",
                        dest="copy_org", default=True,
                        help="copy original path")
        self.OptionParser.add_option("--ofs_incr",
                        action="store", type="float",
                        dest="offset_increase", default=2,
                        help="Offset increase between iterations")




    def effect(self):

        for id, node in self.selected.iteritems():
            if node.tag == inkex.addNS('path','svg'):
                p = cubicsuperpath.parsePath(node.get('d'))

                scale_factor=5.0


                pco = pyclipper.PyclipperOffset()
                
                new = []


                # load in initial paths
                for sub in p:
                    sub_simple = []
                    h1_simple = []
                    h2_simple = []
                    for item in sub:
                        itemx = [float(z)*scale_factor for z in item[1]]
                        sub_simple.append(itemx)
                        #eprint(itemx)
                        #h1_simple.append(item[0]-item[1]) # handle 1 offset
                        #h2_simple.append(item[2]-item[1]) # handle 2 offset

                    pco.AddPath(sub_simple, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)



                # calculate offset paths for different offset amounts
                offset_list = []
                offset_list.append(self.options.init_offset)
                for i in range(0,self.options.count+1):
                    ofs_inc = +math.pow(float(i)*self.options.offset_increase,2)
                    if self.options.offset_increase <0:
                        ofs_inc = -ofs_inc
                    offset_list.append(offset_list[0]+float(i)*self.options.offset+ofs_inc)


                solutions = []
                for offset in offset_list:
                    solution = pco.Execute(offset*scale_factor)
                    solutions.append(solution)
                    if len(solution)<=0:
                        continue # no more loops to go, will provide no results.


                # re-arrange solutions to fit expected format & add to array
                for solution in solutions:
                    for sol in solution:
                        solx = [[float(s[0])/scale_factor, float(s[1])/scale_factor] for s in sol]
                        sol_p = [[a,a,a] for a in solx]
                        sol_p.append(sol_p[0][:])
                        new.append(sol_p)




                # add old, just to keep (make optional!)
                if self.options.copy_org:
                    for sub in p:
                        new.append(sub)

                node.set('d',cubicsuperpath.formatPath(new))


if __name__ == '__main__':
    e = ofsplot()
    e.affect()

