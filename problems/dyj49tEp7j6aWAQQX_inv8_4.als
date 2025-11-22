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
