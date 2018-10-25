#To check swap

##1 Add mode 2
##2 Add time limitation
##3 Improve the way of storing candidates

import sys
from functions import *
from func_check_rules import checkRules

####Get informations
filename_prev = getInfo("file name of previous roster", 1, 0, 0, 0)
filename_this = getInfo("file name of current roster", 1, 0, 0, 0)
month_old = getInfo("previous month", 0, 1, 0, 0)
year_old = getInfo("year of previous month", 0, 0, 1, 0)
month_new = getInfo("current month", 0,1,0,0)
year_new = getInfo("current year", 0,0,1,0)
mainName = getInfo("your name", 0,0,0,1)

### Preprocess the master roster of previous month###
rosters_prev = preprocessRoster(filename_prev)
rosters_this = preprocessRoster(filename_this)


### Get roster of the main person
mainInfo = rosters_this[mainName]
roster_this = mainInfo.roster
try:
	roster_prev = rosters_prev[mainName].roster
except KeyError:
	print "%s is not in last month" % (mainName)
	roster_prev = []

###Ask for inputs
input1 = raw_input("Please enter the start date and end date:")
start_date, end_date = input1.split()
start_date = int(start_date)
end_date = int(end_date)
len_period = end_date - start_date + 1
idx_period = range(start_date-1,end_date)
mode = raw_input("Please choose mode.1: direct exchange, 2: specify work days")

###Swap and check
candidates = []
if mode == '1':
	for name, info in rosters_this.iteritems():
		#print name
		messages = []
		change_period = []
		change_period_cand = []
		if name == mainName:
			continue
		#get roster of candidate
		roster_this_cand = info.roster
		try:
			roster_prev_cand = rosters_prev[name].roster
		except KeyError:
			#print "%s is not in last month" % (name)
			roster_prev_cand = []
		#swap 
		roster_change = roster_this[:]
		roster_change_cand = roster_this_cand[:]
		for idx in idx_period:
			roster_change[idx] = roster_this_cand[idx]
			roster_change_cand[idx] = roster_this[idx]
			change_period.append(roster_this[idx])
			change_period_cand.append(roster_this_cand[idx])
		#Check if the period contains complete sectors first
		if not checkComplete(change_period_cand):
			print "%s" % (name)
			print "NOT ALLOWED: It is not a complete sector"
			continue
		#Check if the changed one is the same as before
		if not checkChange(change_period, change_period_cand):
			print "%s" % (name)
			print "WARNING: Identical roster"
			continue
		#Check if fits all rules
		r, msg = checkRules(roster_change, roster_prev, month_old, year_old, month_new, year_new, roster_this, mainInfo, info)
		if r:
			for m in msg:
				messages.append(m)
		else:
			print "%s, %s not allowed" % (name, mainName)
			print msg
			continue
		r, msg = checkRules(roster_change_cand, roster_prev_cand, month_old, year_old, month_new, year_new, roster_this_cand, info, mainInfo)
		if r:
			output = [name]
			for m in msg:
				if m:
					output.append(m)
			for m in messages:
				if m:
					output.append(m)
			candidates.append(output)
		else:
			print "%s, %s not allowed" % (name, name)
			print msg
			continue
	for c in candidates:
		for n_or_m in c:
			print n_or_m
		print ""
elif mode == '2':
	ind_work = getIndWork(len_period)
	


def getIndWork(len_period):
	ind_work = raw_input("Please enter 1(work) or 0(off)")
	if len(ind_work) == len_period:
		print "incorrect length of indication for work and off"
		ind_work = getIndWork()
	return ind_work

	
#else:
#	print "Incorrect input, please input Y or n"

