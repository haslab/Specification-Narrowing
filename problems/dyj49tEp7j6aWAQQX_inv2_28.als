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

pred S4 { {
	// Every workstation has workers and every worker works in one workstation
	all w: Worker, k: Workstation | w in k.workers
} }

pred S5 { {
	// Every workstation has workers and every worker works in one workstation
  all wst : Workstation , w : Worker| some wst.workers and one workers.wst 

} }

pred S6 { {
	// Every workstation has workers and every worker works in one workstation
  	all wo: Workstation, wor: Worker | some wo.workers and one workers.wor
} }

pred S7 { {
	// Every workstation has workers and every worker works in one workstation
	all w:Worker | w in Workstation.workers
  	
} }

pred S8 { {
	// Every workstation has workers and every worker works in one workstation
	all k: Workstation | some k.workers
  	all w: Worker, k: Workstation | w in k.workers
} }

pred S9 { {
	// Every workstation has workers and every worker works in one workstation
	all w : Workstation | some(w.workers)
  	all w : Worker | lone(workers.w)
} }

pred S10 { {
	// Every workstation has workers and every worker works in one workstation
	all u: Worker | one w: Workstation | u in w.workers
} }

pred S11 { {
	// Every workstation has workers and every worker works in one workstation
	
} }

pred S12 { {
	// Every workstation has workers and every worker works in one workstation
	some Workstation.workers
  	all w : Worker | w in Workstation.workers
} }

pred S13 { {
	// Every workstation has workers and every worker works in one workstation
	all w : Workstation | some w.workers and one ~workers.w
} }

pred S14 { {
	// Every workstation has workers and every worker works in one workstation
	some Workstation.workers and (all w: Worker | one s: Workstation | w in s.workers)
} }

pred S15 { {
	// Every workstation has workers and every worker works in one workstation
	all w : Worker | lone wo: Workstation | w in Workstation.workers and w in wo.workers
} }

pred S16 { {
	// Every workstation has workers and every worker works in one workstation
	all w: Worker, k: Workstation | some k.workers
} }

pred S17 { {
	// Every workstation has workers and every worker works in one workstation
  	all ws: Workstation | ws.workers in Workstation and all w: ws.workers | w in ws


} }

pred S18 { {
	// Every workstation has workers and every worker works in one workstation
	all w : Workstation | some w1 : Worker | w1 in w.workers
  	one w : Workstation | all w1 : Worker | w1 in w.workers
} }

pred S19 { {
	// Every workstation has workers and every worker works in one workstation
	some Workstation.workers
} }

pred S20 { {
	// Every workstation has workers and every worker works in one workstation
	all ws : Workstation |
		one ws.workers and
		all w : Worker | w in Worker and w in ws.workers
} }

pred S21 { {
	// Every workstation has workers and every worker works in one workstation
	all s : Workstation, w: Worker | some s.workers and some workers.w 
} }

pred S22 { {
	// Every workstation has workers and every worker works in one workstation
	all s: Workstation | all w: Worker | w in s.workers
  	all w: Worker | one s: Workstation | w in s.workers
} }

pred S23 { {
	// Every workstation has workers and every worker works in one workstation
  	all wt : Workstation | one w : Worker | w in wt.workers
  	one wt : Workstation | all w : Worker | w in wt.workers

} }

pred S24 { {
	// Every workstation has workers and every worker works in one workstation
  	some w1: Worker | Workstation.workers = w1
} }

pred S25 { {
	// Every workstation has workers and every worker works in one workstation
  	all w : Worker, ws : Workstation | ws in workers.w and lone ws.workers

} }

pred S26 { {
	// Every workstation has workers and every worker works in one workstation
	(all w: Workstation | some w.workers)
	&& (all w: Worker | one (Workstation->Worker).w)
} }

pred S27 { {
	// Every workstation has workers and every worker works in one workstation
	all ws : Workstation | some ws.workers
	one Workstation.workers
} }
