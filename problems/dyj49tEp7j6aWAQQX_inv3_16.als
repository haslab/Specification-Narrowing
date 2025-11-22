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

pred S8 { {
	// Every component is assembled in one workstation
	all c:Component | c.workstation = Workstation
} }

pred S9 { {
	// Every component is assembled in one workstation
    workstation in Component lone -> Workstation
} }

pred S10 { {
	// Every component is assembled in one workstation
	all c : Component | one w : Workstation | c.workstation in w

} }

pred S11 { {
	// Every component is assembled in one workstation
	one x: Workstation|all c:Component | c in workstation.x
} }

pred S12 { {
	// Every component is assembled in one workstation
	one w: Workstation | all c: Component | c in c.workstation
} }

pred S13 { {
	// Every component is assembled in one workstation
	one c : Component | one w : Workstation | w in c
} }

pred S14 { {
	// Every component is assembled in one workstation
  all c: Component | #c.workstation = 2

} }

pred S15 { {
	// Every component is assembled in one workstation
    workstation in Component some -> Workstation
} }
