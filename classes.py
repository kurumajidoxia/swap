class FA():
	def __init__(self, name, position, language, roster, note):
		self.name = name
		self.position = position
		self.language = language
		self.roster = roster
		self.note = note

class Flight():
	def __init__(self, name, cate, SH, SM, EH, EM, ND):
		self.name = name
		self.category = cate
		self.start_hour = SH
		self.start_minute = SM
		self.end_hour = EH
		self.end_minute = EM
		self.next_day = ND
