
import os

ALLOW_EMPTYING = False
ALLOW_POURING = True


class Jug:
	# IMMUTABLE
	def __init__(self, capacity, initial):
		"""
		Capacity and initial liquid content.
		Set capacity to None for infinite capacity.
		Set initial to None for infinite initial content.
		"""
		self.capacity = capacity
		self.amount = initial
	def __repr__(self):
		return "Jug(%s, %s)" % (self.capacity, self.amount)

class JugCollection:
	def __init__(self, jugs):
		self.jugs = jugs
	def successors(self):
		for i, jug in enumerate(self.jugs):
			if jug.amount == 0:
				continue
			
			# Try emptying it
			if ALLOW_EMPTYING:
				if jug.amount is not None:
					Emptied = [jug2 for i2, jug2 in enumerate(self.jugs) if i2 != i]
					Emptied.append(Jug(jug.capacity, 0))
					yield JugCollection(Emptied)

			# Try pouring into another jug
			if ALLOW_POURING:
				for i2, jug2 in enumerate(self.jugs):
					if i2 == i:
						continue
					# Compute available space
					if jug2.capacity is None:
						available_space = None
					else:
						available_space = jug2.capacity - jug2.amount
					if available_space == 0:
						continue
					# Compute first jug's remaining amount, and second jug's new amount
					if jug.amount is None:
						remaining = None
						new_amount = jug2.capacity
					elif available_space is None or available_space >= jug.amount:
						remaining = 0
						if jug2.amount is None:
							new_amount = None
						else:
							new_amount = jug2.amount + jug.amount
					elif available_space < jug.amount:
						remaining = jug.amount - available_space
						new_amount = jug2.capacity
					Poured = [jug3 for i3, jug3 in enumerate(self.jugs) if i3 not in (i, i2)]
					Poured.append(Jug(jug.capacity, remaining))
					Poured.append(Jug(jug2.capacity, new_amount))
					yield JugCollection(Poured)
	def __repr__(self):
		j_reprs = [repr(j) for j in self.jugs]
		j_reprs.sort() # so it's a unique representation for this state, usable for eg checking which states are dead
		return "JugCollection([\n\t" + ',\n\t'.join(j_reprs) + "\n\t])"
	def as_tuple(self):
		capacities_amounts = [(j.capacity, j.amount) for j in self.jugs]
		capacities_amounts.sort(reverse=True)
		return tuple(a for c, a in capacities_amounts)

def breadth_first_search_iteration(steps_states_histories, done_check, dead_signatures):
	steps, state, history = steps_states_histories[0]
	steps_states_histories = steps_states_histories[1:]
	for successor in state.successors():
		if successor.as_tuple() in dead_signatures:
			continue
		if done_check(successor):
			print "DONE, in %s steps" % steps
			print "History:"
			for h in history + [successor]:
				print '\t' + str(h.as_tuple())
			return True, steps_states_histories, dead_signatures
		steps_states_histories.append((steps + 1, successor, history + [successor]))
	dead_signatures.add(state.as_tuple())
	return False, steps_states_histories, dead_signatures

def breadth_first_search(initial_state, done_check):
	steps_states_histories = [(0, initial_state, [initial_state])]
	dead_signatures = set()
	while True:
		found_it, steps_states_histories, dead_signatures = breadth_first_search_iteration(steps_states_histories, done_check, dead_signatures)
		if found_it:
			break
		if not steps_states_histories:
			print "Terminated without finding any solutions."

def state_graph_drawing(initial_state):
	processed_node_names = set()
	to_process = [initial_state]
	edges = []
	while to_process:
		state = to_process[0]
		to_process = to_process[1:]
		if state.as_tuple() in processed_node_names:
			continue
		processed_node_names.add(state.as_tuple())
		for succ in state.successors():
			edges.append((state.as_tuple(), succ.as_tuple()))
			if succ.as_tuple() not in processed_node_names:
				to_process.append(succ)
	outfile = open("jug_drawing.gv", "w")
	outfile.write("digraph StateGraph {\n")
	outfile.write("node [shape=circle]; ")
	for node_name in processed_node_names:
		outfile.write("\"" + str(node_name) + "\"; ")
	outfile.write("\n")
	for (a, b) in edges:
		outfile.write("\"" + str(a) + "\" -> \"" + str(b) + "\";\n")
	outfile.write("\noverlap=false;\n}")
	outfile.close()
	os.system("rm jug_drawing.png")
	os.system("dot -Tpng jug_drawing.gv >jug_drawing.png")
	os.system("eog jug_drawing.png")

# Solve some jug problems
if True:
	initial = JugCollection([	Jug(8, 8),
								Jug(5, 0),
								Jug(3, 0),
								])
	state_graph_drawing(initial)
if False:
	print "\nFirst problem..."
	initial = JugCollection([	Jug(8, 8),
								Jug(5, 0),
								Jug(3, 0),
								])
	breadth_first_search(initial, lambda jc: any(j.amount == 4 for j in jc.jugs))

	print "\nAnother problem..."
	initial = JugCollection([	Jug(8, 8),
								Jug(1, 0),
								])
	breadth_first_search(initial, lambda jc: any(j.amount == 4 for j in jc.jugs))

