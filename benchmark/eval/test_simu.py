import numpy as np
import pandas as pd
import sys
import json
import re


filepath = sys.argv[1]
boxSize = (720,720,1152)
error = False
N_nodes = 8 # Change if deviating from default


try:
	tp = 0
	data = pd.read_csv(filepath + '/out0/output_cells-%05d.csv' % tp,delim_whitespace=True)[7:]
	N_cells = data.shape[0]
	for tp in [0,1,2,3,4]:
		data = pd.read_csv(filepath + '/out0/output_cells-%05d.csv' % tp,delim_whitespace=True)[7:]
		if data.shape[0] != N_cells:
			error = True
			
		if np.sum(data['CenterX'] < 0) > 0 or np.sum(data['CenterY'] < 0) > 0 or np.sum(data['CenterZ'] < 0) > 0:
			error = True
			break
		if np.sum(data['CenterX'] > boxSize[0]) > 0 or np.sum(data['CenterY']  > boxSize[1]) > 0 or np.sum(data['CenterZ']  > boxSize[2]) > 0:
			error = True
			break


    

except FileNotFoundError:
	print('File not found. Simulation incomplete!')
	error = True

print('Error = %s' %(str(error)))
with open(filepath + '/out0/ran_correctly.txt', 'w') as f:
	f.write(str(int(not(error))))

if error == False:

	with open(filepath + '/config.json', 'r') as f:
		config = json.load(f)

	N_MC_steps = config['Settings']['timesteps'] #Should be 5050 by default
	N_tasks = np.product(config['Geometry']['blockcount'])

	with open(filepath + '/job.out', 'r') as f:
		last_line =  (f.read().splitlines())[-1]
		regex_for_time_per_MC = "[0-9][.][0-9]*"
		m = re.search(regex_for_time_per_MC, last_line)
		time_per_MC_step = float(m.group(0))

	df = pd.DataFrame()
	df["Nodes"] = [N_nodes]
	df["Tasks/Node"] = [N_tasks / N_nodes]
	df["Threads/Task"] = [1] #Only included for completeness, should always be 1
	df["Ran correctly"] = [int(not(error))]
	df["time per MC /s"] = [time_per_MC_step]
	df["t_run"] = [time_per_MC_step * N_MC_steps]
	df.to_csv(filepath + '/result.csv')
	print(df.to_string(index=False))
