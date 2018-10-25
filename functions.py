import re
from classes import *
from flights import *

def preprocessRoster(filename):
	data = {}
	count_line = 0
	roster = []
	name = ""
	language = ""
	note = []
	f = open(filename, 'r')
	for line in f:
		count_line += 1
		if count_line == 1:
			info = line.split('|')
			del info[:2]
			del info[-3:]
			for r in info:
				r = r.strip()
				if r:
					roster.append(r)
				else:
					roster.append('000')
		elif count_line == 2:
			name = line.split('|')[1]
			if name.find("PED") != -1:
				name = name.split("PED")[0]
			name = name.strip()
		elif count_line == 3:
			info = line.split('|')
			del info[-3:]
			language = info[1].split(' ')[11]
			del info[:2]
			for remark in info:
				note.append(remark.strip())
		else:
			count_line = 0
			data[name] = FA(name, 'BC', language, roster, note)
			#print name, roster
			note = []
			roster = []
	f.close()
	return data

def getInfo(request, f, month, year, name):
	s = "Please enter " + request + ": "
	info = raw_input(s)
	if f:
		try:
			file_dp = open(info,'r')
		except IOError:
			print "Incorrect file name, please enter again"
			info = getInfo(request, f, month, year, name)
	elif month:
		try:
			info = int(info)
		except ValueError:
			print "Please enter a number between 1-12"
			info = getInfo(request, f, month, year, name)
		else:
			if info < 1 or info > 12:
				print "Please enter a number between 1-12"
				info = getInfo(request, f, month, year, name)
	elif year:
		try:
			info = int(info)
		except ValueError:
			print "Please enter a 4-digit number"
			info = getInfo(request, f, month, year, name)
		else:
			if info < 2018 or info > 2019:
				print "Please enter the correct year"
				info = getInfo(request, f, month, year, name)
	elif name:
		name_pattern = re.compile("([A-Z]+ )+")
		if not name_pattern.match(info):
			print "Please enter name with the format on roster"
			info = getInfo(request, f, month, year, name)
	return info

def checkCategory(roster):
	cate_roster = []
	flight_pattern = re.compile("[0-9]{3}")
	standby_pattern = re.compile("RN[0-9]")
	for r in roster:
		if flight_pattern.match(r):
			flight = flights[r]
			if flight.category == 'SINHKG':
				cate_roster.append(1)
			elif flight.category == 'HKGSIN':
				cate_roster.append(2)
			else:
				print "There is problem to categorize flight %s" % (r)
				return False
		elif standby_pattern.match(r):
			cate_roster.append(3) #standby
		else:
			cate_roster.append(0) #off
	return cate_roster

def checkComplete(roster):
	cate_roster = checkCategory(roster)
	if cate_roster:
		first_cate = cate_roster[0]
		last_case = cate_roster[-1]
		if first_cate == 2 or last_case == 1:
			return False
		else:
			return True
	else:
		return False

def check_work(roster):
	work = []
	flight_pattern = re.compile("[0-9]{3}")
	standby_pattern = re.compile("RN[0-9]")
	training = ['BBC', 'GRA', 'PRB']
	pregnancy = ['NB']
	for r in roster:
		if flight_pattern.match(r) or standby_pattern.match(r) or (r in training) or (r in pregnancy):
			work.append(True)
		else:
			work.append(False)
	return work

def checkChange(period, period_cand):
	work_prd = check_work(period)
	work_prd_cand = check_work(period_cand)
	for i in xrange(len(period)):
		if (period[i] != period_cand[i]) and (work_prd[i] or work_prd_cand[i]):
			return True
	return False









