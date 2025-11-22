sig Workstation { workers : set Worker, succ : set Workstation } one sig begin, end in Workstation {} sig Worker {} sig Human, Robot extends Worker {} abstract sig Product { parts : set Product } sig Material extends Product {} sig Component extends Product { workstation : set Workstation } sig Dangerous in Product {}
pred S0 { {
	// The parts of a component must be assembled before it in the production line
	all c : Component, p : c.parts & Component | c.workstation in p.workstation.^succ
} }

pred S1 { {
	// The parts of a component must be assembled before it in the production line

} }

pred S2 { {
	// The parts of a component must be assembled before it in the production line
	all c: Component | all p: c.parts | p in succ.{c.workstation}
} }

pred S3 { {
	// The parts of a component must be assembled before it in the production line
	all c: Component | all p: c.parts | c.workstation in p.workstation.^succ
 } }

pred S4 { {
	// The parts of a component must be assembled before it in the production line
	all c : Component | c.workstation in c.parts.workstation.^succ
} }

pred S5 { {
    // The parts of a component must be assembled before it in the production line
    all c: Component, p: c.parts | p.workstation in c.workstation.~succ
} }

pred S6 { {
  // The parts of a component must be assembled before it in the production line
  all c:Component | some (c.parts & Component) => c.workstation in c.parts.workstation.^succ

} }

pred S7 { {
	// The parts of a component must be assembled before it in the production line
  all c : Component | c.parts.workstation in c.workstation.^succ
} }

pred S8 { {
	// The parts of a component must be assembled before it in the production line
	
  	all c : Component, p : c.parts, ws1 : p.workstation, ws2 : c.workstation | ws1 in ws2.^succ
} }

pred S9 { {
	// The parts of a component must be assembled before it in the production line
	all c: Component, p: c.parts |
        all ws: c.workstation, wsPart: p.workstation |
            wsPart in ws.(~succ) 
} }

pred S10 { {
	// The parts of a component must be assembled before it in the production line
	
    all c : Component, p : c.parts | 
  		p.workstation in (^succ).c.workstation
  
  
} }

pred S11 { {
  // The parts of a component must be assembled before it in the production line
  all c:Component | c.workstation in c.parts.workstation.*succ 
} }
