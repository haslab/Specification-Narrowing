sig Workstation { workers : set Worker, succ : set Workstation } one sig begin, end in Workstation {} sig Worker {} sig Human, Robot extends Worker {} abstract sig Product { parts : set Product } sig Material extends Product {} sig Component extends Product { workstation : set Workstation } sig Dangerous in Product {}
pred S0 { {
	// Every workstation has workers and every worker works in one workstation
	all ws: Workstation | some ws.workers
  	all w: Worker | one ws: Workstation | w in ws.workers
} }

pred S1 { {
	// Every workstation has workers and every worker works in one workstation
  all wst : Workstation | some wst.workers and one workers.wst 

} }

pred S2 { {
	// Every workstation has workers and every worker works in one workstation
	(all w : Workstation | some w.workers) and (all w1 : Worker | w1 in Workstation.workers)
} }

pred S3 { {
	// Every workstation has workers and every worker works in one workstation
	all k: Workstation | some k.workers
  	
} }
