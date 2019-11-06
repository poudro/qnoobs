#
# Copyright (c) 2017, Stephanie Wehner and Axel Dahlberg
# All rights reserved.
#
# Copyright (c) 2019, Audrey Boixel, Alain Chancé, Daniel Mills and Antoine Sinton
# All rights reserved.  
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. All advertising materials mentioning features or use of this software
#    must display the following acknowledgement:
#    This product includes software developed by Stephanie Wehner, QuTech.
# 4. Neither the name of the QuTech organization nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# adapted from https://github.com/SoftwareQuTech/CQC-Python/blob/master/examples/pythonLib/extendGHZ/charlieTest.py

from cqc.pythonLib import CQCConnection
from simulaqron.toolbox.manage_nodes import NetworksConfigConstructor

def main(agents, idx):
    # Initialize the connection
    with CQCConnection(agents[idx]) as Charlie:

        # Receive qubit
        qC = Charlie.recvQubit()

        qC.H()

        # Measure qubit
        m = qC.measure()

        # TODO(poudro): issue Alice and Bob should not be known by Charlie's but simulaqron internal 
        #               socket handling is blocking and we enter a insolvable situation when a same 
        #               agent is waiting to send and receive from same node
        for i in range(2):
            a = agents[i]

            Charlie.sendClassical(a, m)


if __name__ == "__main__":
    main()
