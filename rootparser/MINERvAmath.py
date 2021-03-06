import numpy as np
import math



#FIXME: where do we put numerical constants
c = 3E8				#speed of light (m/s)
m_p = 938.6			#mass of neutron (MeV/cc)
m_n = 939.3			#mass of neutron (MeV/cc)
BE_p = 200				#Avg binding energy of proton (MeV)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#ROTATIONS, CONVERSIONS


def rot2D_matrix(theta):
#Initialize a rotation matrix for a given theta, IN RADIANS
	return ( (math.cos(theta), math.sin(theta)), (-math.sin(theta), math.cos(theta)) )

#Rotating in a linear world.
THETA = -0.05887
rot_matrix = rot2D_matrix(THETA)

def yz_rotation(p_vec, datatype=0):
#takes a 4vec (E, x, y, z) OR 3vec (x,y,z)
#	datatype indicates how different particles are rotated depending on
#	standards imposed by the higher powers
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

# const double numi_beam_angle_rad = -0.05887;
#
# double fspy_prime = -1.0*sin(numi_beam_angle_rad)*fspz[i] + cos(MinervaUnits::numi_beam_angle_rad)*fspy[i];
#
# double fspz_prime = cos(numi_beam_angle_rad)*fspz[i] + sin(MinervaUnits::numi_beam_angle_rad)*fspy[i];

def convert_E2T(arr, m):
	"""
	Convert the given 4-vector's Energy entry to kinetic energy = E-M
	Should be called after all relativistic calculations are made
	Args:
		arr: an np array representing the 4-vector
		m: The mass of the particle
	"""

	return np.array( [arr[0] - m, arr[1], arr[2], arr[3] ])

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
		#raise ValueError("MakeKineNeutron: Negative Neutron Energy %d calculated. Adjust BE_p" % E_n)
		#log.warning("MakeKineNeutron: Negative Neutron Energy %d calculated. Adjust BE_p" % E_n)
		raise ValueError("MakeKineNeutron: Negative Neutron Energy %d calculated. Adjust BE_p" % E_n)
		return None
#Get kinetic energies of neutrons
	return np.array([E_n, -P_mu[1], -P_mu[2], p_nz])


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def normalize_0(diff):
	#Send [-2pi,2pi] -> [0, 2pi]
	if diff > np.pi:
		diff = diff - 2*np.pi
	elif diff < -np.pi:
		diff = diff + 2*np.pi
	return diff

def normalize_1(diff):
	#send [-pi,pi]->[0, 2pi]
	if diff > 0:
		return diff
	elif diff < 0:
		return diff + 2*np.pi
	return diff

def calculate_phi_T(a,b, normalize=0):
	#calculate the angle between the xy-plane projections of a and b (3vecs)
	#This is a CLOCKWISE ANGLE FROM A->B
	if len(a) > 3 or len(b) > 3:
		raise ValueError("compare_vecs requires 3-vectors for comparison")
	phi_a = np.arctan2(a[1], a[0])
	phi_b = np.arctan2(b[1], b[0])
	#diff = max(phi_a, phi_b) - min(phi_a, phi_b)
	if normalize==0:
		diff = normalize_0(phi_a-phi_b)
	elif normalize==1:
		diff = normalize_1(phi_a-phi_b)

	return np.degrees(diff)

def calculate_theta_Tx(a,b):
	#Calculate the angle between the XZ projections of a and b (3vecs)
	theta_aX = np.arctan2(a[0], a[2])
	theta_bX = np.arctan2(b[0], b[2])
	diff = normalize_0(theta_aX - theta_bX)
	return np.degrees(diff)

def calculate_theta_Ty(a,b):
	#Calculate the angle between the YZ projections of a and b (3vecs)
	theta_aY = np.arctan2(a[1], a[2])
	theta_bY = np.arctan2(b[1], b[2])
	diff = normalize_0(theta_aY - theta_bY)
	return np.degrees(diff)

def compare_vecs(a, b, mode=0):
#Given two spacial 3vecs (unnormalized), compares angle between them
#	mode=0: return angle, separation
#	mode=1: return cos(angle), separation
#Pass this v_n*time and vec(vtx->blob) in (m)
	if len(a) > 3 or len(b) > 3:
		raise ValueError("compare_vecs requires 3-vectors for comparison")
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
