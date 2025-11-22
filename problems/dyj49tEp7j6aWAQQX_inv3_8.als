sig Workstation { workers : set Worker, succ : set Workstation } one sig begin, end in Workstation {} sig Worker {} sig Human, Robot extends Worker {} abstract sig Product { parts : set Product } sig Material extends Product {} sig Component extends Product { workstation : set Workstation } sig Dangerous in Product {}
pred S0 { {
	// Every component is assembled in one workstation
	all c: Component | one c.workstation
} }

pred S1 { {
	// Every component is assembled in one workstation
	all c: Component | one w: Workstation | c in w.workstation
} }

pred S2 { {
	// Every component is assembled in one workstation

} }

pred S3 { {
	// Every component is assembled in one workstation
	all c : Component | some c.workstation
} }

pred S4 { {
	// Every component is assembled in one workstation
    all c : Component | one Workstation 
} }

pred S5 { {
	// Every component is assembled in one workstation
	all c : Component | lone c.workstation
} }

pred S6 { {
	// Every component is assembled in one workstation
	one Component.workstation
} }

pred S7 { {
	// Every component is assembled in one workstation
    workstation in Component one -> Workstation
} }
