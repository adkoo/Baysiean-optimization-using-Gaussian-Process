# -*- coding: iso-8859-1 -*-

#INSTRUCTIONS FOR USE:
#This code will run an offline example as-is without any input arguments. Simply run the file in python.

#In order to use it on a specific machine --
#1) First read 'HOW_TO_USE.txt' and complete steps 1 and 2
    #Note: It is recommended to make a copy of this file with a unique name and open it so that you don't edit the original.
#2) Then, on line 23 of this file, select the name of your .npy file  (created in step 2 of 'HOW_TO_USE.txt') that contains your desired scan params.
#3) On line 24, choose if you want results saved by setting saveResultsQ = True/False
    #Note: If saveResultsQ is set to True, the scan data will be saved to the local directory called 'saved_results' and will have filename formatted as 'scan_YYYY-MM-DD-hhmmss.npy'
#4) Now choose the condition on which to stop the scan by replacing line 50 with your desired expression

#The script should now be ready to be run. It will try to optimize your target function.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import logging
logging.basicConfig(level=logging.WARN)

from modules.bayes_optimization import BayesOpt, negUCB, negExpImprove
from modules.OnlineGP import OGP
import numpy as np
import os,sys
import importlib
# mi_module = importlib.import_module('machine_interfaces.machine_interface_example')
# import machine_interfaces.topas_interface as mi_module
import time
import matplotlib.pyplot as plt

# Import the topas interface:
try:
    sys.path.append(os.path.realpath('../Phaser_Models'))
    from topas import BayesianOptimiser_MachineInterface as mi_module
except:
    logging.error(f'Failed to import the topas machine interface; probably you need to adjust the system path.'
                  f'\nThis code expects the Phaser_Models repository to be stored in the same directory as this repository')
    sys.exit()



if __name__ == '__main__':
    BaseDirectory = os.path.expanduser("~") + '/Dropbox (Sydney Uni)/Projects/PhaserSims/topas'
    SimulationName = 'BayesianOptimisationTest'
    scan_params_filename = 'TopasOptimiserParams.npy'
    saveResultsQ = False
    #
    #load the dict that contains the parameters for the scan (control pv list, starting settings, and gp hyperparams)
    scan_params = np.load('params/'+scan_params_filename, allow_pickle=True).item()

    #how long to wait between acquisitions
    acquisition_delay = scan_params['acquisition_delay']

    #create the machine interface
    dev_ids = ['dev_ids']
    start_point = scan_params['start_point'] #if start_point is set to None, the optimizer will start from the current device settings.
    mi = mi_module.machine_interface(scan_params, BaseDirectory, SimulationName,debug=False) #an isotropic n-dimensional gaussian with amplitude=1, centered at the origin, plus gaussian background noise with std dev = 0.1

    #create the gp
    ndim = len(scan_params['dev_ids'])
    gp_precisionmat = scan_params['gp_precisionmat']
    gp_amp = scan_params['gp_amp']
    gp_noise = scan_params['gp_noise'] #std
    hyps = [gp_precisionmat, np.log(gp_amp), np.log(gp_noise**2)] #format the hyperparams for the OGP
    gp = OGP(ndim, hyps)

    #create the bayesian optimizer that will use the gp as the model to optimize the machine
    opt = BayesOpt(gp, mi, acq_func="UCB", start_dev_vals = mi.x, dev_ids = scan_params['dev_ids'])
    opt.ucb_params = scan_params['ucb_params'] #set the acquisition function parameters

    #run the gp search for some number of steps
    Obj_state_s=[]

    for i in range(5):
        print('iteration =', i)
        print('current position:', mi.x, 'current objective value:', mi.getState()[1][0])
        try:
            Obj_state_s.append(mi.getState()[1][0])
        except:
            logging.error('something fd up!')
        opt.OptIter()
        # time.sleep(acquisition_delay)



