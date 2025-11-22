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

pred S12 { {
	// The parts of a component must be assembled before it in the production line
  all c: Component | all p: c.parts | 
        some ps, pc: Workstation | 
            ps in p.workstation and 
            pc in c.workstation and 
            ps in pc.^succ

} }

pred S13 { {
	// The parts of a component must be assembled before it in the production line
	all a, b: Component | a in b.parts implies b in a.workstation.^succ
} }

pred S14 { {
	// The parts of a component must be assembled before it in the production line
  all c: Component | let
		ws = c.workstation,
		prevParts = (ws.succ.parts - c.parts) | 
		prevParts not in ws.parts

} }

pred S15 { {
    
    
    all c : Component , p : c.parts | 
            some wsPart, wsComponent : Workstation | 
                p in workstation.wsPart and 
                c in workstation.wsComponent and
                wsComponent in wsPart.^succ
} }

pred S16 { {
	// The parts of a component must be assembled before it in the production line
    all c: Component | c.parts not in c.workstation.^succ


} }

pred S17 { {
  // The parts of a component must be assembled before it in the production line
  all c:Component | some (c.parts & Component) => c.workstation in  c.parts.workstation.*succ

} }

pred S18 { {
  // The parts of a component must be assembled before it in the production line
  all c:Component | some (c.parts & Component) => c.workstation in c.^parts.workstation.^succ

} }

pred S19 { {
	// The parts of a component must be assembled before it in the production line
	all c: Component, p: c.parts |
        some ws: c.workstation, wsPart: p.workstation |
            wsPart in ws.(~succ) 
} }

pred S20 { {
	// The parts of a component must be assembled before it in the production line
  
	all c:Component | no (workstation.(c.workstation.^succ) & c.^parts)
} }

pred S21 { {
	// The parts of a component must be assembled before it in the production line
	all c : Component, p : (c.parts) | no( c.workstation.succ & p.workstation.succ)
} }

pred S22 { {
	// The parts of a component must be assembled before it in the production line
	all c: Component | one ws1: Workstation | ws1 in c.workstation => all p: c.parts | one ws2: Workstation | ws2 in p.workstation
} }

pred S23 { {
	// The parts of a component must be assembled before it in the production line
	all c: Component, p: c.parts | c.workstation in p.workstation.*succ

} }
