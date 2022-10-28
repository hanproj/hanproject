Instructions for running the code:

1. Compiler + version number
The code was written using Python 3.6.8 on Windows 10/cygwin

2. What libraries need to be installed + version numbers
	altair, v4.10
	altair_viewer, v4.0
	anytree, v2.8.0
	cydifflib, v1.0.1
	infomap, v2.3.0
	llist, v0.7.1
	matplotlib, v3.3.4
	networkx, v2.5
	nx_altair, v0.1.6
	poepy, v0.20	
	PyQt5, v5.15.6
	pyvis, v0.2.0	
	simple_colors, v0.1.5
	sinopy, v0.3.4

3. What dirs need to be downloaded; what the file structure looks like
Need to download:
	hanproj
	hanproj/hanproject (this is where the code lives)
	hanproj/mirrors (mirror data)
	hanproj/received-shi (received-shi data)
	hanproj/stelae (stelae data)
	hanproj/phonological_data (Schuessler data)
	hanproj/combo (output for combined data)
	 
4. Quick start
Run the process_all_data_sets() function in the soas_data_processing.py file.
This will output network data to your default browser. Annotated poem data can be found in the data directories. So, annotated stelae poems will be in hanproj/stelae. There will be poems annotated by the naive, schuessler, and community (called com_det) annotators.

Here is the comments for the process_all_data_sets() function.
#
# Purpose:
#   This function does pre-community detection (pre-com det) and post-community detection (post-com det) processing
#   on all data sets:
# Input:
#     received_shi (the Lu1983 data; 逯欽立《先秦漢魏晉南北朝詩》1983)
#     mirrors (the kyomeishusei2015 data; 林裕己《漢三國西晉鏡銘集成》2015)
#     stelae (the mao2008 data; 毛遠明《漢魏六朝碑刻校注》2008)
# Output:
#   I. Various networks are output to the system's default web browser
#     For each data set:
#       pre-com det network (monochrome)
#       pre-com det network (colored using post-com det groups as basis for different colors)
#       post-com det network
#   II. Annotated poems
#     For each data set (output to each data type's directory):
#       Naively annotated poems
#       Schuessler annotated poems
#       Community annotated poems (i.e., annotated using the results of community detection)
#   III. Combined Data (combo data)
#     In addition to the singular data types, there is also a combined data type which is output, basically,
#     all of the input data is put into a single network.
#
# This function is set up to run all data types. However, there are a set of flags which can be set to individually
# select which data to run:
#   run_lu1983_data = True
#   run_mirror_data = True
#   run_stelae_data = True
#   run_combined_data = True
#
#   Setting any of these to False will turn off their respective processing.