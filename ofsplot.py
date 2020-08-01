#!/usr/bin/env python3

import inkex
import math
from inkex.paths import CubicSuperPath
import re
import pyclipper

class ofsplot(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.arg_parser.add_argument("--count", type=int, dest="count", default=10, help="Number of offset operations")
        self.arg_parser.add_argument("--ofs", type=float, dest="offset", default=2, help="Offset amount")
        self.arg_parser.add_argument("--init_ofs", type=float, dest="init_offset", default=2, help="Initial Offset Amount")
        self.arg_parser.add_argument("--copy_org", type=inkex.Boolean, default=True, help="copy original path")
        self.arg_parser.add_argument("--ofs_incr", type=float, dest="offset_increase", default=2, help="Offset increase between iterations")

    def effect(self):
        for id, node in self.svg.selected.items():
            if node.tag == inkex.addNS('path','svg'):
                p = CubicSuperPath(node.get('d'))

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

                node.set('d',CubicSuperPath(new))

if __name__ == '__main__':
    ofsplot().run()
