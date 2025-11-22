sig Workstation { workers : set Worker, succ : set Workstation } one sig begin, end in Workstation {} sig Worker {} sig Human, Robot extends Worker {} abstract sig Product { parts : set Product } sig Material extends Product {} sig Component extends Product { workstation : set Workstation } sig Dangerous in Product {}
pred S0 { {
	// Humans and robots cannot work together
	all w: Workstation, h: Human, r: Robot | (h in w.workers) implies (r not in w.workers)
    
  	
  	
} }

pred S1 { {
	// Humans and robots cannot work together
  	all w:Workstation | no (w.workers & Human & Robot)
} }

pred S2 { {
	// Humans and robots cannot work together
	all w: Workstation | (Human in w.workers) implies (Robot not in w.workers)
  	
} }

pred S3 { {
	// Humans and robots cannot work together
    all w: Workstation, workers: w.workers | workers in Human or workers in Robot 
} }

pred S4 { {
	// Humans and robots cannot work together
	all ws : Workstation | some w : Worker | w in Human implies ws in workers.w or 
  	w in Robot implies ws in workers.w
} }

pred S5 { {
	// Humans and robots cannot work together
	no disj w1, w2: Worker | w1 in Human and w2 in Robot
} }

pred S6 { {
	// Humans and robots cannot work together
	all w : Workstation | w.workers in Human implies w.workers not in Robot 
} }

pred S7 { {
	// Humans and robots cannot work together
	all w: Workstation | (Human & Robot) not in w.workers
} }

pred S8 { {
	// Humans and robots cannot work together
	all y1,y2: Worker, x: Workstation | (y1 in x.workers) and(y1 in Human) implies (y2 not in x.workers) and (y2 not in Robot)  

  

  all r: Robot, h:Human, x:Workstation | x in workers.r implies x not in workers.h
} }

pred S9 { {
	// Humans and robots cannot work together
	all h:Human, r:Robot |some workers.h implies no workers.r
} }

pred S10 { {
	// Humans and robots cannot work together
	all w: Workstation | no w.workers & (Human + Robot)
} }

pred S11 { {
	// Humans and robots cannot work together
	all w: Workstation | (Human in w.workers) <=> (Robot not in w.workers)
  	
  
} }

pred S12 { {
	// Humans and robots cannot work together
  all w : Workstation | w.workers = Human or w.workers = Robot
} }

pred S13 { {
	// Humans and robots cannot work together
  	
  	
	all ws: Workstation | one h: Human| (h in ws.workers) implies ws.workers in Human
} }

pred S14 { {
	
  	all ws: Workstation + Workstation.succ | one p:ws.workers | p in Human implies ws.workers in Human
} }

pred S15 { {
	// Humans and robots cannot work together
	Workstation.workers in Human or Workstation.workers in Robot
} }

pred S16 { {
	// Humans and robots cannot work together
	all ws: Workstation | ws.workers not in (Human + Robot)
} }

pred S17 { {
	// Humans and robots cannot work together
	all ws : Workstation | some w : Worker | w in ws.workers implies w in Human or w in Robot
} }

pred S18 { {
	// Humans and robots cannot work together
	all wo : Workstation | all w : Worker, r : Robot | (wo in workers.w implies wo not in workers.r)
  
} }

pred S19 { {
	// Humans and robots cannot work together
  	all w1,w2:Worker, wk:Workstation | w1 in wk.workers and w2 in wk.workers implies 
 w1 in Human and w2 in Robot or w1 in Robot and w2 in Human
} }
