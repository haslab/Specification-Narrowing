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

pred S8 { {
	// Workers are either human or robots
	Worker in Human or Worker in Robot
} }

pred S9 { {
	// Workers are either human or robots
  all w : Worker | w in Human
	
} }

pred S10 { {
	// Workers are either human or robots
  all w : Workstation | w.workers = Human + Robot
	
} }

pred S11 { {
	// Workers are either human or robots
	all w: Workstation | w.workers in (Human + Robot) and some w.workers and no Worker
} }

pred S12 { {
	// Workers are either human or robots
	Workstation.workers = Human + Robot
} }

pred S13 { {
	// Workers are either human or robots
	all u: Worker | Human in u or Robot in u
} }

pred S14 { {
	// Workers are either human or robots
  	Workstation.workers + Workstation.^succ.workers in Human or Workstation.workers + Workstation.^succ.workers in Robot
  	
} }

pred S15 { {
	// Workers are either human or robots
	Worker-(Human+Robot) & Workstation.workers = none
} }

pred S16 { {
	// Workers are either human or robots
	all w: Workstation | (w.workers not in Human) or (w.workers not in Robot)
} }

pred S17 { {
	// Workers are either human or robots
  	all ws: Workstation.^succ, w: ws.workers | w in Human or w in Robot
	
} }

pred S18 { {
	// Workers are either human or robots
	all w : Worker | w not in Human and w not in Robot
} }

pred S19 { {
	// Workers are either human or robots
	all w : Worker | w in Human or w !in Robot
} }

pred S20 { {
	// Workers are either human or robots
  all w : Workstation | Human in w.workers  or Robot in w.workers
} }

pred S21 { {
	// Workers are either human or robots
  	all w: Workstation | Worker !in w.workers
	
} }

pred S22 { {
	// Workers are either human or robots
  	all w: Workstation | (Human in Worker implies Human in w.workers) 
	or (Robot in Worker implies Robot in w.workers) and lone w.workers and Worker in w.workers
	
} }

pred S23 { {
	// Workers are either human or robots
  	all w: Workstation | (Human in Worker implies Human in w.workers) 
	and (Robot in Worker implies Robot in w.workers) and lone w.workers and Worker in w.workers
	
} }

pred S24 { {
	// Workers are either human or robots
	all w: Workstation | w.workers in (Human + Robot)
  	all h: Human | h in workers.h
} }

pred S25 { {
	// Workers are either human or robots
	all w: Workstation | w.workers in (Human + Robot)
  	all H: Human | some w: Workstation | H in w.workers
} }

pred S26 { {
	// Workers are either human or robots
  	all ws: Workstation, w: ws.workers | w in Human and w not in Robot
	
} }

pred S27 { {
	// Workers are either human or robots
  	all ws: Workstation| (ws.workers in Human and ws.workers not in Robot) or (ws.workers not in Human and ws.workers in Robot)
	
} }
