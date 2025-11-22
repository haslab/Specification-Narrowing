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

pred S4 { {
	// Workers are either human or robots
  all w:Workstation | w.workers in Robot or w.workers in Human
	
} }

pred S5 { {
	// Workers are either human or robots
  	all e : Worker | e=Human or e=Robot 
	
} }

pred S6 { {
	// Workers are either human or robots
	all w: Workstation | w.workers in Human + Robot and some w.workers
} }

pred S7 { {
	// Workers are either human or robots
	all w : Worker | w = Human + Robot
} }
