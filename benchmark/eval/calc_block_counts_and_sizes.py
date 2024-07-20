import itertools
import argparse
import numpy as np
import json

def get_prime_factors(n):#Brute force prime-factorization algorithm
    i = 2
    factors = []
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return factors

def check_if_valid_count(system_size, blockcounts):
	size_x,size_y,size_z = system_size
	count_x, count_y, count_z = blockcounts
	if size_x % count_x == 0 and size_y % count_y == 0 and size_z % count_z == 0:
		return True
	else:
		return False
    
def calc_block_counts_and_sizes(N_cores,system_size):

    primes = get_prime_factors(N_cores)
    N_per_dim = np.floor(len(primes)/3)
    N_per_dims_global = 3*[N_per_dim]
    while sum(N_per_dims_global) < len(primes):
        N_per_dims_global[2] += 1

    all_possible_counts = []

    # Get all possible combinations of 3 numbers obtained by splitting the prime factors into 3 subsets and multipying them 
    for N_per_dims in set(itertools.permutations(N_per_dims_global)):
        for iteration in set(itertools.permutations(primes)):        
            x = int(np.product(iteration[:int(N_per_dims[0])]))
            y = int(np.product(iteration[int(N_per_dims[0]):int(N_per_dims[0]+N_per_dims[1])]))
            z = int(np.product(iteration[int(N_per_dims[0]+N_per_dims[1]):]))
            
            if check_if_valid_count(system_size,(x,y,z)) == True:#We only store those combinations which are valid for our system size
                all_possible_counts.append((x,y,z))


    mean_sizes = []#Stores the mean blocksize for each blockcount combination
    all_possible_counts = list(set(all_possible_counts))
    
    for blockcount in all_possible_counts:
        blocksize = np.array(system_size) / np.array(blockcount)
        mean_sizes.append(np.mean(blocksize))

    if len(mean_sizes) > 0:
        index = np.argmin(mean_sizes)
        blockcounts_final = all_possible_counts[index]
        blocksize_final = np.array(system_size) / np.array(blockcounts_final)
        blocksize_final = [int(val) for val in blocksize_final]#Need integers for json file
        return {
                "blockcounts" : blockcounts_final,
                "blocksizes" : blocksize_final
                }        
    else:
        print("No valid splitting for this number of cores and system size! Please retry with different core number.")
        return None



parser = argparse.ArgumentParser()
parser.add_argument('-N', '--NCPUs',type = int, default = 384,help="Overall number of CPUs, i.e. N_cores_per_node * N_nodes")  # Overall number of CPUs, i.e. N_cores_per_node * N_nodes
parser.add_argument('-c', '--config', type = str, default='src/config.json', help="Location of config.json")  # Location of config.json
parser.add_argument('-u', '--update_config', action='store_true',help="Flag for enabling automatic config updating")  # Flag for enabling automatic config updating
args = parser.parse_args()

system_size = [720,720,1152]
N_cores = args.NCPUs
configuration = calc_block_counts_and_sizes(N_cores,system_size)
if isinstance(configuration,dict):
	print(f"The following configuration will work for {N_cores} cores.")
	print(" \"blockcount\": ", configuration['blockcounts'])
	print(" \"blocksize\": ", configuration['blocksizes'])

	if args.update_config:
		import jsbeautifier
		#Update the config
		with open(args.config,'r') as f:
			config = json.load(f)	
		config['Geometry']['blockcount'] = configuration['blockcounts']
		config['Geometry']['blocksize'] = configuration['blocksizes']
		options = jsbeautifier.default_options()
		options.indent_size = 4
		config_pretty = jsbeautifier.beautify(json.dumps(config), options)
		with open(args.config,'w') as f:
			f.write(config_pretty)
else:
	pass
