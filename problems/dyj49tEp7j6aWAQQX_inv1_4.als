sig Workstation { workers : set Worker, succ : set Workstation } one sig begin, end in Workstation {} sig Worker {} sig Human, Robot extends Worker {} abstract sig Product { parts : set Product } sig Material extends Product {} sig Component extends Product { workstation : set Workstation } sig Dangerous in Product {}
pred S0 { {
	// Workers are either human or robots
 all w: Worker | w in Human or w in Robot
} }

pred S1 { {
	// Workers are either human or robots
	
} }

pred S2 { {
	// Workers are either human or robots
	all w: Workstation | w.workers in Human + Robot
} }

pred S3 { {
	// Workers are either human or robots
 all w: Worker | w in Human and w in Robot
} }
