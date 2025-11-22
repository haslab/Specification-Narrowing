sig Workstation { workers : set Worker, succ : set Workstation } one sig begin, end in Workstation {} sig Worker {} sig Human, Robot extends Worker {} abstract sig Product { parts : set Product } sig Material extends Product {} sig Component extends Product { workstation : set Workstation } sig Dangerous in Product {}
pred S0 { {
	// Dangerous components cannot be assembled by humans
	all c: (Component & Dangerous) | no c.workstation.workers & Human
} }

pred S1 { {
	// Dangerous components cannot be assembled by humans
    
} }

pred S2 { {
	// Dangerous components cannot be assembled by humans
	all o: Component | (o in Dangerous) implies (Human not in o.workstation.workers)
} }

pred S3 { {
	// Dangerous components cannot be assembled by humans
  	all d:Dangerous| d.workstation.workers not in Human
} }

pred S4 { {
	// Dangerous components cannot be assembled by humans
  all c:Component | (c in Dangerous) implies (c.workstation.workers in Human)

} }

pred S5 { {
	// Dangerous components cannot be assembled by humans
	all o: Component | (o in Dangerous) implies (Robot in o.workstation.workers)
} }

pred S6 { {
	// Dangerous components cannot be assembled by humans
  	
  all c:Component| c.workers in Human implies c in Dangerous
} }

pred S7 { {
	// Dangerous components cannot be assembled by humans
	all c: Component, ws: Workstation |
  		ws.workers in Human => c not in Dangerous
} }

pred S8 { {
	// Dangerous components cannot be assembled by humans
  
  
  all c:Component | all work: c.workstation | c in Dangerous implies Human not in work.workers
  
} }

pred S9 { {
	// Dangerous components cannot be assembled by humans
	all c : Component, w : Workstation | c in Dangerous implies no (w.workers & Human)
} }

pred S10 { {
	// Dangerous components cannot be assembled by humans
  all c: Component | some c.parts & Dangerous => no c.workstation.workers & Human

} }

pred S11 { {
	// Dangerous components cannot be assembled by humans
  all h : Human, p : Product | p in Dangerous implies no workers.h

} }

pred S12 { {
	// Dangerous components cannot be assembled by humans
  all c: Component| all w: Worker| c in Dangerous iff w in Human
  
} }

pred S13 { {
	// Dangerous components cannot be assembled by humans
	all o: Component | (o in Dangerous) implies (Robot in o.workstation.workers)
  	all o: Component | (o in Dangerous) implies (Human not in o.workstation.workers)
} }

pred S14 { {
	// Dangerous components cannot be assembled by humans
	all x: Workstation | workstation.x in (Component & Dangerous) implies x.workers not in Human
} }

pred S15 { {
	// Dangerous components cannot be assembled by humans
    workers.Human & Dangerous.parts.workstation = none
} }

pred S16 { {
	// Dangerous components cannot be assembled by humans
  all c : Component | no c.workstation.workers & Human

} }

pred S17 { {
	// Dangerous components cannot be assembled by humans
	all c: Component | (c in Dangerous) implies all w: Worker | w in Worker - Human
} }

pred S18 { {
	// Dangerous components cannot be assembled by humans
  	all d:Dangerous| Human not in d.workstation.workers
} }

pred S19 { {
	// Dangerous components cannot be assembled by humans
	all c : Component | c in Dangerous implies no (c.workstation.workers)

} }

pred S20 { {
	// Dangerous components cannot be assembled by humans
	all c: Component | all r: Robot | all w: Workstation |( c in Dangerous and w in c.workstation )implies r in w.workers
} }

pred S21 { { 
	// Dangerous components cannot be assembled by humans
	all c: Component | all wo: Workstation |all p: Product | all w: Worker| p in Dangerous and p in c.parts and wo in c.workstation and w in wo.workers implies w in Robot
} }

pred S22 { {
	// Dangerous components cannot be assembled by humans
	all o: Component | (o in Dangerous) implies (Human not in o.workstation)
} }

pred S23 { {
	// Dangerous components cannot be assembled by humans
  
  
  all c:Component | all work: c.workstation | Human not in work.workers implies c in Dangerous 
} }

pred S24 { {
	// Dangerous components cannot be assembled by humans
  
  
  all c:Component | all work: c.workstation | c in Dangerous iff Human not in work.workers and Robot in work.workers
  
} }

pred S25 { {
	// Dangerous components cannot be assembled by humans
        all w : Workstation, c : (Component & Dangerous) | w.workers in Robot


} }

pred S26 { {
	// Dangerous components cannot be assembled by humans
  	Human not in (parts.Dangerous).workers

} }

pred S27 { {
	// Dangerous components cannot be assembled by humans
  	(parts.Dangerous).workers not in Human

} }
