import re

from flights import *
from datetime import datetime, timedelta
from functions import check_work

def checkRule_1A_1B(roster_change, roster_this, roster_prev, month_old, year_old, month_new, year_new):
	msg = []
	dt = []
	for i in xrange(len(roster_change)):
		dt.append(datetime(year_new, month_new, i+1))
	if roster_prev:
		roster_old = roster_prev[-1:] + roster_this
		roster_new = roster_prev[-1:] + roster_change
		dt.insert(0, datetime(year_old, month_old, len(roster_prev)))
	else:
		roster_old = roster_this
		roster_new = roster_change
	work_old = check_work(roster_old)
	work_new = check_work(roster_new)
	
	#Check if swap a flight which duty ends after 2300
	for i, r in enumerate(work_old):
		if i == 0:  #skip first item
			continue
		if not r:   #it's a day off
			if work_new[i-1] and roster_new[i-1] != roster_old[i-1]:
				flight = flights[roster_new[i-1]]
				curfew = dt[i-1].replace(hour=23)
				if flight.next_day:
					end_time = dt[i-1].replace(day=i, hour=flight.end_hour, minute=flight.end_minute)
				else:
					end_time = dt[i-1].replace(hour=flight.end_hour, minute=flight.end_minute)
				if end_time > curfew:
					msg = "NOT ALLOWED: duty end time beyond 2300 before a day off is not allowed to be swapped on %s" %(dt[i-1].date())
					return False, msg
	#Check local night rules
	len_roster = len(work_new)
	for i, r in enumerate(work_new):
		if (i == 0): #skip first item
			continue
		if not r: #it's an off day
			if work_new[i-1]: #previous day is a work day
				# check Day1 local night
				flight_pre = flights[roster_new[i-1]]
				if flight_pre.next_day:
					d = dt[i-1].day + 1
				else:
					d = dt[i-1].day
				end_time = dt[i-1].replace(day=d, hour=flight_pre.end_hour, minute=flight_pre.end_minute)
				offday_morning = dt[i].replace(hour=8)
				duration = offday_morning - end_time
				if (duration.total_seconds() / 3600) < 8.0:
					msg = "NOT ALLOWED: No local night from %s to %s" %(dt[i-1].date(), dt[i].date())
					return False, msg
				# check Day2 local night
				num_off = 1  #numer of day off
				at_least = 35.0
				idx_nf = i+1 #index of next flight
				while (idx_nf < len_roster) and (not work_new[idx_nf]):
					num_off += 1
					at_least += 24.0
					idx_nf += 1
				if idx_nf == len_roster: #no next flight in current roster
					return True, msg
				flight_next = flights[roster_new[idx_nf]]
				start_time = dt[idx_nf].replace(hour=flight_next.start_hour, minute=flight_next.start_minute)
				offday_night = dt[idx_nf-1].replace(hour=22)
				duration = start_time - offday_night
				if (duration.total_seconds() / 3600) < 8.0:
					msg = "NOT ALLOWED: No local night from %s to %s" %(dt[idx_nf-1].date(), dt[idx_nf].date())
					return False, msg
				# check 35 hours (only for single day off)
				if num_off > 1:
					continue
				duration_35 = start_time - end_time
				if (duration_35.total_seconds() / 3600) < at_least:
					msg = "NOT ALLOWED: Doesn't meet 35-hour requirement from %s to %s" %(dt[i-1].date(), dt[idx_nf].date())
					return False, msg
	return True, msg
def checkRule_1C(roster_change, roster_prev, month_old, year_old, month_new, year_new):
	allow = True
	msg = []
	dt_new = []
	dt_old = []
	work_new = check_work(roster_change)
	for i in xrange(len(work_new)):
		dt_new.append(datetime(year_new, month_new, i+1))
	if roster_prev:
		work_old = check_work(roster_prev)
		for i in xrange(len(work_old)):
			dt_old.append(datetime(year_old, month_old, i+1))
		work = work_old[-6:] + work_new
		roster = roster_prev[-6:] + roster_change
		dt = dt_old[-6:] + dt_new
	else:
		work = work_new
		roster = roster_change
		dt = dt_new
	count = 0
	for i, day in enumerate(work):
		if day:
			count += 1
			if count == 6:
				if i == (len(work)-1): #skip the last day
					continue
				try:
					flight = flights[roster[i]]
				except KeyError:
					print "No %s in flights dictionary" %(roster[i])
					sys.exit()
				else:
					if (flight.end_hour > 17) or (flight.end_hour == 17 and flight.end_minute > 0) or flight.next_day:
						msg = "NOT ALLOWED: duty end after 17:00 on sixth day on %s"% (dt[i].date())
						allow = False
						return allow, msg
					elif roster[i+1] == 'SB':
						msg = "NOT ALLOWED: SB can not be critical day off on %s" %(dt[i+1].date())
						allow = False
						return allow, msg
			elif count == 7:
				msg = "NOT ALLOWED: work for 7 days in a row"
				allow = False
				return allow, msg
		else:
			count = 0
	return allow, msg
def checkRule_1D(roster_change, roster_prev, month_old, year_old, month_new, year_new):
	allow = True
	msg = []
	dt_new = []
	dt_old = []
	work_new = check_work(roster_change)
	for i in xrange(len(work_new)):
		dt_new.append(datetime(year_new, month_new, i+1))
	if roster_prev:
		work_old = check_work(roster_prev)
		for i in xrange(len(work_old)):
			dt_old.append(datetime(year_old, month_old, i+1))
		work = work_old[-13:] + work_new
		roster = roster_prev[-13:] + roster_change
		dt = dt_old[-13:] + dt_new
	else:
		work = work_new
		roster = roster_change
		dt = dt_new
	count_total = 0
	count_off = 0
	for i, day in enumerate(work):
		if day:
			count_off = 0
			count_total += 1
			if count_total == 12:
				try:
					flight = flights[roster[i]]
				except KeyError:
					print "No %s in flights dictionary" %(roster[i])
					sys.exit()
				else:
					if (flight.end_hour > 17) or (flight.end_hour == 17 and flight.end_minute > 0) or flight.next_day:
						msg = "NOT ALLOWED: duty end after 17:00 on twelfth day on %s" %(dt[i].date())
						allow = False
						return allow, msg
					elif roster[i+1] == 'SB':
						msg = "NOT ALLOWED: SB can not be critical day off on %s" %(dt[i+1].date())
						allow = False
						return allow, msg
					elif roster[i+2] == 'SB':
						msg = "NOT ALLOWED: SB can not be critical day off on %s" %(dt[i+2].date())
						allow = False
						return allow, msg
			if count_total == 13:
				msg = "NOT ALLOWED: no consecutive off days in 14 days"
				allow = False
				return allow, msg
		else:
			if count_off >= 1:
				count_off += 1
				if count_off >= 2:
					count_total = 0
			else:	
				count_total += 1
				count_off += 1
	return allow, msg
def checkRule_1E(roster_change, roster_prev, month_old, year_old, month_new, year_new):
	allow = True
	msg = []
	dt_new = []
	dt_old = []
	work_new = check_work(roster_change)
	for i in xrange(len(roster_change)):
		dt_new.append(datetime(year_new, month_new, i+1))
	if roster_prev:
		work_old = check_work(roster_prev)
		for i in xrange(len(roster_prev)):
			dt_old.append(datetime(year_old, month_old, i+1))
		work = work_old + work_new
		dt = dt_old + dt_new
	else:
		work = work_new
		dt = dt_new
	total_days = len(work)
	last_index = total_days- 28
	for i in xrange(last_index):
		list_28 = work[i:i+27]
		count_off = list_28.count(False)
		if count_off < 7:
			msg = "NOT ALLOWED: less than 7 days off from %s to %s" %(dt[i].date(), dt[i+27].date())
			allow = False
			return allow, msg
	return allow, msg
def checkRule_2(roster_change, roster_prev, month_old, year_old, month_new, year_new):
	allow = True
	msg = []
	dt_new = []
	dt = []
	for i in xrange(len(roster_change)):
		dt_new.append(datetime(year_new, month_new, i+1))
	if roster_prev:
		work = check_work(roster_prev[-1:] + roster_change )
		roster = [roster_prev[-1]] + roster_change
		dt = [datetime(year_old, month_old, len(roster_prev))] + dt_new
	else:
		work = check_work(roster_change)
		roster = roster_change
		dt = dt_new
	for i, day in enumerate(work):
		if i == (len(work) - 1): #skip last day
			continue
		if day and work[i+1]:
			flight = flights[roster[i]]
			if flight.next_day:
				d = dt[i] + timedelta(days=1)
			else:
				d = dt[i]
			end_time = d.replace(hour=flight.end_hour, minute=flight.end_minute)
			flight = flights[roster[i+1]]
			start_time = dt[i+1].replace(hour=flight.start_hour, minute=flight.start_minute)
			rest = start_time - end_time
			if (rest.total_seconds() / 3600) < 13.0:
				msg = "NOT ALLOWED: rest time is less than 13 hours from %s to %s" %(dt[i].date(), dt[i+1].date())
				allow = False
				return allow, msg
	return allow, msg

def checkRule_6(roster_change, roster_prev, month_old, year_old, month_new, year_new):
	allow = True
	msg = []
	dt_new = []
	dt_old = []
	for i in xrange(len(roster_change)):
		dt_new.append(datetime(year_new, month_new, i+1))
	if roster_prev:
		roster = roster_prev + roster_change
		for i in xrange(len(roster_prev)):
			dt_old.append(datetime(year_old, month_old, i+1))
		dt = dt_old + dt_new
	else:
		roster = roster_change
		dt = dt_new
	count = 0
	day_off = ['G', 'SB']
	for i, r in enumerate(roster):
		if r in day_off:
			count +=1
			if count > 9:
				msg = "NOT ALLOWED: consecutive days off (G or SB) exceed 9 days from %s to %s" %(dt[i-9].date(), dt[i].date())
				allow = False
				return allow, msg
		else:
			count = 0
	return [allow,msg]
	
#def checkRule_7(roster_change, roster_prev, info):
#	allow = True
#	msg = []
#	if roster_prev:
#		roster = roster_prev + roster_change
#	else:
#		roster = roster_change
#	
#	leave_day = False
#	count = 0
#	day_off = ['G', 'SB']
#	leave = ['LP', 'LS', 'LT', 'L']
#	for i, r in enumerate(roster):
#		if r in leave:
#			leave_day = i+1
#			break
#	if leave_day:
#		idx_leave = leave_day -1
#		if idx_leave < 10 or idx_leave > (len(roster) - 10):
#			msg = "WARNING: not enough information to check number of days off attached to leave. Please check roster of %s manually" %(info.name)
#			return allow, msg
#		roster_leave = roster[idx_leave:]
#		for i, r in enumerate(roster_leave):
#			if r in leave:
#				continue
#			else:
#				idx_end_leave = i
#				break
#		idx_end_leave += idx_leave 
#		before_leave = roster[:idx_leave]
#		before_leave.reverse()
#		after_leave = roster[idx_end_leave:]
#		for i, r in enumerate(before_leave):
#			if r in day_off:
#				count += 1
#			else:
#				break
#		for i, r in enumerate(after_leave):
#			if r in day_off:
#				count += 1
#			else:
#				break
#		if count > 9:
#			msg = "NOT ALLOWED: no. days off attached to leave exceeds 9 days"
#			allow = False
#			return allow, msg
#	return allow, msg

def checkRule_8(info_home, info_guest):
	allow = True
	msg = []
	FA_home = info_home.name
	lang_home = info_home.language
	lang_guest = info_guest.language
	require_lan = ['MD', 'CT']
	if (lang_home != lang_guest) and (lang_home in require_lan):
		msg = "WARNING: please cehck flights of %s manually, it might not meet language requirement" %(FA_home)
		return allow, msg
	return allow, msg
		
def checkRule_9(roster_this, roster_change, info):
	allow = True
	msg = []
	not_allowed = ['RR', 'RV','MF', 'CO', 'FD', 'FS', 'SN', 'UC', 'PT', 'AEP', 'WS', 'TIP', 'SA', 'DC', 'LP', 'LS', 'LT', 'L', 'BBC', 'GRA','USL', 'CTT', 'PX', 'FD','0','ZZ', 'TG']
	note = info.note
	change = []
	for i in xrange(len(roster_this)):
		change.append(roster_this[i] != roster_change[i])
	for i, c in enumerate(change):
		if c:
			if (roster_this[i] in not_allowed) or \
				(note[i] in not_allowed):
				msg = "NOT ALLOWED: %s is not allowed to be swapped"%\
													(roster_this[i])
				allow = False
				return allow, msg
	return allow, msg

#P.S. part of restriction of rule 13 is wriiten in 1C and 1D
def checkRule_13(roster_this, roster_prev, roster_change):
	allow = True
	msg = []
	if roster_prev:
		roster_old = roster_prev[-1:] + roster_this
		roster_new = roster_prev[-1:] + roster_change
		change = [False]
	else:
		roster_old = roster_this
		roster_new = roster_change
		change = []
	standby_pattern = re.compile("RN[0-9]") 
	for i in xrange(len(roster_this)):
		change.append(roster_this[i] != roster_change[i])
	for i, c in enumerate(change):
		if c and roster_old[i] == 'SB' and \
			standby_pattern.match(roster_old[i-1]) and \
			not change[i-1] and roster_new[i] != 'G':
			msg = "NOT ALLOWED: SB attached to standby can not be swapped away"
			allow = False
			return allow, msg
	return allow, msg

def checkRules(roster_change, roster_prev, month_old, year_old, month_new, year_new, roster_this, info_home, info_guest):
	msg = []
	r, m = checkRule_1A_1B(roster_change, roster_this, roster_prev, month_old, year_old, month_new, year_new)
	if r:
		if m:
			msg.append(m)
	else:
		return False, m
	r, m = checkRule_1C(roster_change, roster_prev, month_old, year_old, month_new, year_new)
	if r:
		if m:
			msg.append(m)
	else:
		return False, m
	r, m = checkRule_1D(roster_change, roster_prev, month_old, year_old, month_new, year_new)
	if r:
		if m:
			msg.append(m)
	else:
		return False, m
	r, m = checkRule_1E(roster_change, roster_prev, month_old, year_old, month_new, year_new)
	if r:
		if m:
			msg.append(m)
	else:
		return False, m
	r, m = checkRule_2(roster_change, roster_prev, month_old, year_old, month_new, year_new)
	if r:
		if m:
			msg.append(m)
	else:
		return False, m
	r, m = checkRule_6(roster_change, roster_prev, month_old, year_old, month_new, year_new)
	if r:
		if m:
			msg.append(m)
	else:
		return False, m
#	r, m = checkRule_7(roster_change, roster_prev, info_home)
#	if r:
#		if m:
#			msg.append(m)
#	else:
#		return False, m
	r, m = checkRule_8(info_home, info_guest)
	if r:
		if m:
			msg.append(m)
	else:
		return False, m
	r, m = checkRule_9(roster_this, roster_change, info_home)
	if r:
		if m:
			msg.append(m)
	else:
		return False, m
	r, m = checkRule_13(roster_this, roster_prev, roster_change)
	if r:
		if m:
			msg.append(m)
	else:
		return False, m
	
	return True, msg

















