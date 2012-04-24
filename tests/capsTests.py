#
# Copyright 2012 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA
#
# Refer to the README and COPYING files for full details of the license
#

import os
from testrunner import VdsmTestCase as TestCaseBase

import caps


class TestCaps(TestCaseBase):

    def testCpuInfo(self):
        testPath = os.path.realpath(__file__)
        dirName = os.path.split(testPath)[0]
        path = os.path.join(dirName, "cpu_info.out")
        c = caps.CpuInfo(path)
        self.assertEqual(c.cores(), 12)
        self.assertEqual(c.sockets(), 2)
        self.assertEqual(set(c.flags()), set("""fpu vme de pse tsc msr pae
                                                mce cx8 apic mtrr pge mca
                                                cmov pat pse36 clflush dts
                                                acpi mmx fxsr sse sse2 ss ht
                                                tm pbe syscall nx pdpe1gb
                                                rdtscp lm constant_tsc
                                                arch_perfmon pebs bts
                                                rep_good xtopology
                                                nonstop_tsc aperfmperf pni
                                                pclmulqdq dtes64 monitor
                                                ds_cpl vmx smx est tm2 ssse3
                                                cx16 xtpr pdcm dca sse4_1
                                                sse4_2 popcnt aes lahf_lm
                                                arat epb dts tpr_shadow vnmi
                                                flexpriority ept
                                                vpid""".split()))
        self.assertEqual(c.mhz(), '2533.402')
        self.assertEqual(c.model(),
                        'Intel(R) Xeon(R) CPU           E5649  @ 2.53GHz')
