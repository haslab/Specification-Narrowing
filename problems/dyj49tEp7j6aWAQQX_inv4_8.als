sig Workstation { workers : set Worker, succ : set Workstation } one sig begin, end in Workstation {} sig Worker {} sig Human, Robot extends Worker {} abstract sig Product { parts : set Product } sig Material extends Product {} sig Component extends Product { workstation : set Workstation } sig Dangerous in Product {}
pred S0 { {
	// Components must have parts and materials have no parts
	all c: Component | some c.parts
    all m: Material | no m.parts
} }

pred S1 { {
  // Components must have parts and materials have no parts
  all c: Component, m: Material | some c.parts and no m.parts
} }

pred S2 { {
	// Components must have parts and materials have no parts
	all c: Component | some c.parts and all m: Material | no m.parts
} }

pred S3 { {
	// Components must have parts and materials have no parts

} }

pred S4 { {
	// Components must have parts and materials have no parts
	all p:Product | some p.parts implies p in Component 

} }

pred S5 { {
	// Components must have parts and materials have no parts
	all o: Component | some o.parts
} }

pred S6 { {
	// Components must have parts and materials have no parts
	(some Component.parts) and (no Material.parts)
} }

pred S7 { {
	// Components must have parts and materials have no parts
	all p: Material | p.parts not in Product
  	all p: Component | p.parts in Product
} }
