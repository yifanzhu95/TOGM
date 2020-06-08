#main file planning trajectories
#using trajoptlib
import sys, os, time
import numpy as np
import matplotlib.pyplot as plt
import logging
from trajoptlib.io import get_onoff_args
from trajoptlib import System, NonLinearPointObj, LqrObj
from trajoptlib import LinearConstr,NonLinearObj
from trajoptlib import TrajOptProblem
from trajoptlib import OptConfig, OptSolver
from trajoptlib.utility import show_sol
from scipy.sparse import coo_matrix
import math
from robosimian_GM_simulation import robosimianSimulator
import pdb
import configs
from klampt.math import vectorops as vo
import copy
class Robosimian(System):
	def __init__(self):
		System.__init__(self,nx=30,nu=12,np=0,ode='Euler')
		q_2D = np.array([0.0,1.02,0.0] + [0.6- 1.5708,0.0,-0.6]+[0.6+1.5708,0.0,-0.6]+[0.6-1.5708,0.0,-0.6] \
	 		+[0.6+1.5708,0.0,-0.6])[np.newaxis].T
		q_dot_2D = np.array([0.0]*15)[np.newaxis].T
		self.robot = robosimianSimulator(q= q_2D,q_dot = q_dot_2D,dt = 0.005,solver = 'cvxpy', augmented = True)

	def dyn(self,t,x,u,p=None):  
		a = self.robot.getDyn(x,u) #This is a numpy column 2D vector N*1
		return np.concatenate([x[15:30],a]) #1D numpy array


	def jac_dyn(self, t, x, u, p=None):

		a,J_tmp = self.robot.getDynJac(x,u)
		a = np.concatenate([x[15:30],np.ravel(a)])		
		J = np.zeros((30,1+30+12))
		J[:,1:43] = J_tmp
		return a,J

	###older version that uses naive FD for dynamics
	# def jac_dyn(self, t, x, u, p=None):
	# 	a = np.ravel(self.robot.getDyn(x,u))
	# 	a = np.concatenate([x[15:30],a])		

	# 	#Forward Finite Difference to get the 
	# 	eps = 1e-4
	# 	J = np.zeros((30,1+30+12))
	# 	for i in range(30):
	# 		FD_vector = np.zeros(30)
	# 		FD_vector[i] = eps
	# 		tmp_x = np.add(x,FD_vector)
	# 		tmp_a = self.robot.getDyn(tmp_x,u)
	# 		J[:,i+1] = np.multiply(np.subtract(np.concatenate([tmp_x[15:30],np.ravel(tmp_a)]),a),1.0/eps)
	# 	for i in range(12):
	# 		FD_vector = np.zeros(12)
	# 		FD_vector[i] = eps
	# 		tmp_u = np.add(u,FD_vector)
	# 		tmp_a = self.robot.getDyn(x,tmp_u)
	# 		J[:,i+1+30] = np.multiply(np.subtract(np.concatenate([x[15:30],np.ravel(tmp_a)]),a),1.0/eps)
	# 	#print("Jac done")
	# 	#maybe convert J to coomatrix
	# 	return a,J



#These are the force and torque that could support the robot in place.
# single_traj_guess = [0,0.915,0,-0.9708,0,-0.6,2.1708,0,-0.6,-0.9708,0,-0.6,2.1708,0,-0.6]+[0.0]*15
# single_u_guess = configs.u_augmented_mosek


sys = Robosimian()
global N
N = 181 #9s trajectory 0.05s
t0 = 0.0
tf = 0.05*(N-1)
#This uses direct transcription
problem = TrajOptProblem(sys,N,t0,tf,gradmode = True)
# penetrationConstr = penetrationConstraint(30)
# problem.add_constr(penetrationConstr,path = True)


#### different setttings start from here
#####setting 7
# R = np.array([1.0]*12)
# cost = LqrObj(R = R)#,ubase = np.array(single_u_guess))
# diff = [0.3]*15
# problem.xbd = [np.array(vo.sub(single_traj_guess[0:15],diff) + [-2]*15),np.array(vo.add(single_traj_guess[0:15],diff) + [2]*15)]
# problem.ubd = [np.array([-1000]*12),np.array([1000]*12)]
# problem.x0bd = [np.array(single_traj_guess),np.array(single_traj_guess)]
# problem.xfbd = [np.array(single_traj_guess),np.array(single_traj_guess)] #just stay in place...

#####setting 8&9&10
# Q = np.array([0]*15 + [1.0]*15)
# cost = LqrObj(Q = Q)#,ubase = np.array(single_u_guess))
# diff = [0.3]*15
# problem.xbd = [np.array(vo.sub(single_traj_guess[0:15],diff) + [-2]*15),np.array(vo.add(single_traj_guess[0:15],diff) + [2]*15)]
# problem.ubd = [np.array([-1000]*12),np.array([1000]*12)]
# problem.x0bd = [np.array(single_traj_guess),np.array(single_traj_guess)]
# problem.xfbd = [np.array(vo.sub(single_traj_guess[0:15],diff) + [-2]*15),np.array(vo.add(single_traj_guess[0:15],diff) + [2]*15)]

#####setting 11
# Here we have the toros basically shifting forward
# x_base = np.array([0.0]*15 + [0.1] + [0.0]*14)
# Q = np.array([0.0]*15 + [10.0]*3 + [0.01]*12)
# cost = LqrObj(Q = Q,xbase = x_base)#,ubase = np.array(single_u_guess))
# diff = [2]*15
# #be lax on the x bounds
# problem.xbd = [np.array(vo.sub(single_traj_guess[0:15],diff) + [-2]*15),np.array(vo.add(single_traj_guess[0:15],diff) + [2]*15)]
# problem.ubd = [np.array([-100]*12),np.array([100]*12)]

# x0lower = vo.sub(single_traj_guess,[0]+[0.005]*14+[2]*15)
# x0upper = vo.add(single_traj_guess,[0]+[0.005]*14+[2]*15)
# problem.x0bd = [np.array(x0lower),np.array(x0upper)]
# problem.xfbd = [np.array(vo.sub(single_traj_guess[0:15],diff) + [-2]*15),np.array(vo.add(single_traj_guess[0:15],diff) + [2]*15)]


#####This is for setting 12
# diff = [2]*15
# diff[1] = 0.25 #small z change
# diff[2] = 0.8 #small torso angle change
# problem.xbd = [np.array(vo.sub(single_traj_guess[0:15],diff) + [-2]*15),np.array(vo.add(single_traj_guess[0:15],diff) + [2]*15)]
# problem.ubd = [np.array([-100]*12),np.array([100]*12)]
# #diff[2] = 0.1 #horizontal torso angle at the start of the traj
# problem.x0bd = [np.array(vo.sub(single_traj_guess[0:15],diff) + [-2]*15),np.array(vo.add(single_traj_guess[0:15],diff) + [2]*15)]
# problem.xfbd = [np.array(vo.sub(single_traj_guess[0:15],diff) + [-2]*15),np.array(vo.add(single_traj_guess[0:15],diff) + [2]*15)]

######setting 14
problem.xbd = [np.array([-0.2,0.4,-0.3] + [-math.pi]*12 + [-3]*15),np.array([5,1.1,0.3] + [math.pi]*12 + [3]*15)]
problem.ubd = [np.array([-300]*12),np.array([300]*12)]
problem.x0bd = [np.array([-0.05,0.4,-0.3] + [-math.pi]*12 + [-0.2]*15),np.array([0.05,1.1,0.3] + [math.pi]*12 + [0.2]*15)]
problem.xfbd = [np.array([0.3,0.4,-0.3] + [-math.pi]*12 + [-2]*15),np.array([5,1.1,0.3] + [math.pi]*12 + [2]*15)]




class cyclicConstr(LinearConstr):
	def __init__(self):
		global N
		dmin = 0.3
		dmax = 1.0
		nX = 30
		nU = 12
		nP = 0
		A = np.zeros((nX,N*(nX+nU+nP)))
		lb = np.zeros(nX)
		ub = np.zeros(nX)
		#enough x translation
		A[0,0] = -1.0
		A[0,0+(N-1)*(nX+nU+nP)] = 1.0
		lb[0] = dmin
		ub[0] = dmax
		#Remain same for the other state dimensions
		for i in range(nX):
			if i > 0:
				A[i,i] = 1.0
				A[i,i+(N-1)*(nX+nU+nP)] = -1.0
		LinearConstr.__init__(self,A,lb = lb,ub = ub)

class transportationCost(NonLinearObj):
	def __init__(self):
		self.nX = 30
		self.nU = 12
		self.nP = 0
		global N
		self.N = N
		self.first_q_dot = 18
		self.NofJoints = 12
		self.first_u = 30
		NonLinearObj.__init__(self,nsol = self.N*(self.nX+self.nU+self.nP),nG = self.N*(self.nX+self.nU)-self.N*self.first_q_dot +2  )

		#print(self.N*(self.nX+self.nU)-self.N*self.first_q_dot +2)
	def __callg__(self,x, F, G, row, col, rec, needg):
		effort_sum = 0.0
		for i in range(self.N):
			for j in range(self.NofJoints):
				#q_dot * u
				effort_sum = effort_sum + (x[i*(self.nX+self.nU+self.nP)+self.first_q_dot+j]*\
					x[i*(self.nX+self.nU+self.nP)+self.first_u+j])**2
		F[:] = effort_sum/(x[(self.N-1)*(self.nX+self.nU+self.nP)]-x[0])
		if needg:
			Gs = []
			nonzeros = [0]
			# for i in range(self.N):
			# 	for j in range(self.first_q_dot):
			# 		G[i*(self.nX+self.nU+self.nP)+j] = 0.0
			Gs.append(effort_sum/(x[(self.N-1)*(self.nX+self.nU+self.nP)]-x[0])**2)
			#G[0] = effort_sum/(x[(self.N-1)*(self.nX+self.nU+self.nP)]-x[0])**2
			#G[(self.N-1)*(self.nX+self.nU+self.nP)] = -effort_sum/(x[(self.N-1)*(self.nX+self.nU+self.nP)]-x[0])**2
			d = x[(self.N-1)*(self.nX+self.nU+self.nP)]-x[0]
			for i in range(self.N-1):
				for j in range(self.NofJoints):
					# G[i*(self.nX+self.nU+self.nP)+self.first_q_dot+j] = 2.0*x[i*(self.nX+self.nU+self.nP)+self.first_q_dot+j]*\
					# 	x[i*(self.nX+self.nU+self.nP)+self.first_u+j]**2
					Gs.append(2.0/d*x[i*(self.nX+self.nU+self.nP)+self.first_q_dot+j]*\
						x[i*(self.nX+self.nU+self.nP)+self.first_u+j]**2)
					nonzeros.append(i*(self.nX+self.nU+self.nP)+self.first_q_dot+j)
				for j in range(self.NofJoints):
					# G[i*(self.nX+self.nU+self.nP)+self.first_q_dot+j+self.NofJoints] = 2.0*x[i*(self.nX+self.nU+self.nP)+self.first_q_dot+j]**2*\
					# 	x[i*(self.nX+self.nU+self.nP)+self.first_u+j]
					Gs.append(2.0/d*(x[i*(self.nX+self.nU+self.nP)+self.first_q_dot+j]**2)*\
						x[i*(self.nX+self.nU+self.nP)+self.first_u+j])
					nonzeros.append(i*(self.nX+self.nU+self.nP)+self.first_q_dot+j+self.NofJoints)
			Gs.append(-effort_sum/(x[(self.N-1)*(self.nX+self.nU+self.nP)]-x[0])**2)
			nonzeros.append((self.N-1)*(self.nX+self.nU+self.nP))
			for i in [self.N-1]:
				for j in range(self.NofJoints):
					Gs.append(2.0/d*x[i*(self.nX+self.nU+self.nP)+self.first_q_dot+j]*\
						x[i*(self.nX+self.nU+self.nP)+self.first_u+j]**2)
					nonzeros.append(i*(self.nX+self.nU+self.nP)+self.first_q_dot+j)
				for j in range(self.NofJoints):
					Gs.append(2.0/d*(x[i*(self.nX+self.nU+self.nP)+self.first_q_dot+j]**2)*\
						x[i*(self.nX+self.nU+self.nP)+self.first_u+j])
					nonzeros.append(i*(self.nX+self.nU+self.nP)+self.first_q_dot+j+self.NofJoints)
			G[:] = Gs
			if rec:
				row[:] = [0]
				col[:] = nonzeros

#####Original setting
# R = np.array([1.0]*12)
# cost = LqrObj(R = R)#,ubase = np.array(single_u_guess))
# problem.xbd = [np.array([-0.5,0.85,-1,-1.57-0.7,-0.7,-0.7,1.57-0.7,-0.7,-0.7,-1.57-0.7,-0.7,-0.7,1.57-0.7,-0.7,-0.7] + [-2]*15),\
# 	np.array([0.5,1.2,1,-1.57+1,0.7,0.7,1.57+1,0.7,0.7,-1.57+0.7,0.7,0.7,1.57+1,0.7,0.7] + [2]*15)]
# problem.ubd = [np.array([-1000]*12),np.array([1000]*12)]
# problem.x0bd = [np.array([0,0.936,0,-0.9708,0,-0.6,2.1708,0,-0.6,-0.9708,0,-0.6,2.1708,0,-0.6]+[0.0]*15),\
# 	np.array([0,0.936,0,-0.9708,0,-0.6,2.1708,0,-0.6,-0.9708,0,-0.6,2.1708,0,-0.6]+[0.0]*15)] 
# #problem.xfbd = [np.array([1.0,0.936,0]+[-10.0]*12 + [0.0]*15),np.array([1.0,0.936,0]+[10.0]*12 +[0.0]*15)] ## set the goal here 
# problem.xfbd = [np.array([0,0.936,0]+[-10.0]*12 + [0.0]*15),np.array([0.0,0.936,0]+[10.0]*12 +[0.0]*15)] #just stay in place...


#settings 7-11
#problem.add_lqr_obj(cost)

#setting 12
# c = transportationCost()
# constr1 = cyclicConstr()
# problem.addNonLinearObj(c)
# problem.addLinearConstr(constr1)

#settting 14
c = transportationCost()
problem.addNonLinearObj(c)

startTime = time.time()
problem.preProcess()
print('preProcess took:',time.time() - startTime)
#print_level 1 for SNOPT is verbose enough
#print_level 0-12 for IPOPT 5 is appropriate, 6 more detailed
cfg = OptConfig(backend='snopt', print_file='temp_files/tmp.out', print_level = 1, opt_tol = 1e-4, fea_tol = 1e-4)
slv = OptSolver(problem, cfg)

#setting 12
#slv.solver.setWorkspace(4000000,5000000)

#setting 14
slv.solver.setWorkspace(7000000,8000000)

startTime = time.time()


# #setting 1-13
# traj_guess = []
# u_guess = []
# for i in range(N):
# 	tmp = copy.copy(single_traj_guess)
# 	tmp[0] = i*0.002
# 	traj_guess.append(tmp)
# 	u_guess.append(single_u_guess)
#guess = problem.genGuessFromTraj(X= np.array(traj_guess), U=np.array(u_guess), t0 = 0, tf = tf)

#setting 14
traj_guess = np.hstack((np.load('results/PID_trajectory/2/q_init_guess.npy'),np.load('results/PID_trajectory/2/q_dot_init_guess.npy')))
u_guess = np.load('results/PID_trajectory/2/u_init_guess.npy')
guess = problem.genGuessFromTraj(X= traj_guess, U= u_guess, t0 = 0, tf = tf)

result = problem.parseF(guess)
#print(result)
#pdb.set_trace()
#print(guess)
rst = slv.solve_guess(guess)

#rst = slv.solve_rand()
print('Took', time.time() - startTime)
print("========results=======")
print(rst.flag)
print(rst.fval,np.shape(rst.fval))
print(rst.sol,np.shape(rst.sol))
print(np.shape(rst.lmd))
sol = problem.parse_sol(rst.sol.copy())
print(sol)

np.save('temp_files/solution_u',sol['u'])
np.save('temp_files/solution_x',sol['x'])
# if rst.flag == 1:
# 	print(rst.flag)
# 	sol = problem.parse_sol(rst.sol.copy())
# 	show_sol(sol)