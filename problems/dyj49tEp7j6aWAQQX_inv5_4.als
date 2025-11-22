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
