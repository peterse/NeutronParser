import numpy as np
import math


#FIXME: where do we put numerical constants
c = 3E8				#speed of light (m/s)
m_p = 938.6			#mass of neutron (MeV/cc)
m_n = 939.3			#mass of neutron (MeV/cc)
BE_p = 200				#Avg binding energy of proton (MeV)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def rot2D_matrix(theta):
#Initialize a rotation matrix for a given theta, in radians
	return ( (math.cos(theta), -math.sin(theta)), (math.sin(theta), math.cos(theta)) )

#Rotating in a linear world.
THETA = 0
rot_matrix = rot2D_matrix(THETA)

def yz_rotation(p_vec):
#takes a 4vec (E, x, y, z) OR 3vec (x,y,z)
#Returns the vector rotated according to Z-tilt of MINERvA
	dims = len(p_vec)
	if dims == 4:
		zpyp = (p_vec[3], p_vec[2]) #(z, y)
	elif dims == 3:
		zpyp = (p_vec[2], p_vec[1])
	#code golf!
	#cor_zy2 = tuple([sum([a*b for a,b in zip(zpyp, i)]) for i in self.rot_matrix])
	#Explicit switch
	cor_zy = [0, 0]
	for i, rot_tup in enumerate(rot_matrix):
		#Matrix multiplication / linear alg
		cor_zy[i] = sum([a*b for a,b in zip(zpyp, rot_tup)])
	cor_zy = tuple(cor_zy) #(z', y')

	if dims == 4:
		return (p_vec[0], p_vec[1], cor_zy[1], cor_zy[0])
	elif dims == 3:
		return (p_vec[0], cor_zy[1], cor_zy[0])



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#Particle attributes

def get_mass(part):
#Return the mass of a 4vec (E, px, py, pz)
	sqrs = map(lambda x: x*x, part.P)
	try:
		return np.sqrt(sqrs[0] - sum(sqrs[1:]))
	#Return imaginary number if norm(E) < norm(p)
	except ValueError:
		return complex(0,abs(sqrs[0] - sum(sqrs[1:]))**.5)

def get_u(vec):
	#u ~ v/c: returns the velocity and speed given a 4vec
	#return type: np.array
	p = np.array(vec[1:])
	v = p*c/ vec[0]
	return v

def norm(vec):
	#Euclidean norm of a 3-vector
	#Arg type: np.array
	return np.linalg.norm(vec)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#"Simulated" particles

#FIXME: numpy functions for speedup
def make_neutron_P(P_mu):
#Using deterministic QE kinematics calculate a neutrons
#Takes in muon 4vec, mc or recon
#Return type: np.array

	#Define some kinematic values
	A = (P_mu[3] + m_p - BE_p - P_mu[0])
	B = (P_mu[1]**2 + P_mu[2]**2 + m_n**2)

	#Simple calculations of neutron kinematics (see Peters, 2016)
	E_n = (B + A**2)/(2*A)
	p_nz = (B - A**2) / (2*A)
	if E_n < 0:
		raise ValueError("MakeKineNeutron: Negative Neutron Energy %d calculated. Adjust BE_p" % E_n)
		return None
#Get kinetic energies of neutrons
	return (E_n - m_n, -P_mu[1], -P_mu[2], p_nz)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def compare_vecs(a, b, mode=0):
#Given two spacial 3vecs (unnormalized), compares angle between them
#	mode=0: return angle, separation
#	mode=1: return cos(angle), separation
#Pass this v_n*time and vec(vtx->blob) in (m)
	norm_a = norm(a)
	norm_b = norm(b)
	a = np.array(a)
	b = np.array(b)
	dot = np.dot(a,b)
	#law of cosines
	cos = dot/(norm_a*norm_b)
	theta = np.degrees(np.arccos(cos))
	d = np.sqrt(norm_a*norm_a + norm_b*norm_b - 2*dot)
	#Return the angle
	if mode==0:
		return theta, d
	#Return the cosine of the angle
	elif mode==1:
				return cos, d
			#print norm_a
