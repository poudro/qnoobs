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

import simulaqron.network
from threading import Thread
import random
import math

from cqc.pythonLib import CQCConnection, qubit

import alice
import bob
import charlie


# TODO(poudro): move to seperate file
class RandomBit():
	def __init__(self):
		self.n = simulaqron.network.Network(name="randomBit", nodes=["randomBit"], force=True)
		self.n.start()
		self.n.running

	def stop(self):
		self.n.stop()

	def get(self):
		m = 0
		with CQCConnection("randomBit", network_name="randomBit") as randomBit:
			q = qubit(randomBit)
			q.H()
			m = q.measure()

		return m


# TODO(poudro): make this a cli parameter
N_AGENTS = 4

def createNet():
	agents = ["agent%s" % (x) for x in range(N_AGENTS)]
	n = simulaqron.network.Network(name="default", nodes=agents, force=True)
	n.start()
	n.running
	return n, agents

# TODO(poudro): move to seperate file
def anonEntanglement(agents):
	threads = []
	print(agents)
	for a in range(N_AGENTS):
		if a == 0:
			threads.append(Thread(target = alice.main, args=(agents,)))
		elif a == 1:
			threads.append(Thread(target = bob.main, args=(agents,)))
		else:
			threads.append(Thread(target = charlie.main, args=(agents,a)))

	for t in threads:
		t.start()

	for t in threads:
		t.join()


### VERIFICATION
# TODO(poudro): extract verification to own file
def generateAngles(n) :
    sumN = 0
    arrayN = []
    for i in range(n -1):
        floatRandom = random.uniform(0, math.pi)
        sumN += floatRandom
        arrayN.append(floatRandom)
    
    M = math.ceil(sumN / math.pi)
    arrayN.append(M * math.pi - sumN)
    
    return arrayN, M

def transform(q, angle):
	step = int(angle * 256 / (2 * math.pi))
	q.H()
	q.rot_X(step)
	q.rot_Y(step)
	q.rot_Z(step)
	return q

def verifyVerifier(agents, verifier):
	with CQCConnection(agents[verifier]) as Verifier:
		angles, M = generateAngles(len(agents))

		for i in range(len(angles)):
			if i != verifier:
				Verifier.sendClassical(agents[i], angles[i])


		q = qubit(Verifier)
		q = transform(q, angles[verifier])
		Y = q.measure()

		for i in range(len(angles)):
			if i != verifier:
				Y += list(Verifier.recvClassical())[0]

		print("Y,M", Y, M)

def verifyReceiver(agents, verifier, receiver):
	with CQCConnection(agents[receiver]) as Receiver:
		angle = list(Receiver.recvClassical())[0]

		q = qubit(Receiver)
		q = transform(q, angle)
		m = q.measure()

		Receiver.sendClassical(agents[verifier], m)

def verification(r, agents):
	verifier = sum([r.get() for i in range(len(agents))])

	threads = []
	for a in range(len(agents)):
		if a == verifier:
			threads.append(Thread(target = verifyVerifier, args=(agents, verifier)))
		else:
			threads.append(Thread(target = verifyReceiver, args=(agents, verifier, a)))

	for t in threads:
		t.start()

	for t in threads:
		t.join()
### END VERIFICATION



if __name__ == '__main__':
	r = RandomBit()
	n, agents = createNet()
	for i in range(50):
		verification(r, agents)

	# anonEntanglement(agents)
	# # ana()

	# # # print(n.running)
	# # r = RandomBit()
	# # for i in range(100):
	# # 	print(r.get())

	n.stop()
	r.stop()