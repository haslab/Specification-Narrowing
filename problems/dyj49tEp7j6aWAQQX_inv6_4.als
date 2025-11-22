sig Workstation { workers : set Worker, succ : set Workstation } one sig begin, end in Workstation {} sig Worker {} sig Human, Robot extends Worker {} abstract sig Product { parts : set Product } sig Material extends Product {} sig Component extends Product { workstation : set Workstation } sig Dangerous in Product {}
pred S0 { {
	// Components cannot be their own parts
	all c: Component | c not in c.^parts
} }

pred S1 { {
  // Components cannot be their own parts
  all c: Component | c not in c.parts
} }

pred S2 { {
	// Components cannot be their own parts
    all c:Component | c not in c.*(parts)

} }

pred S3 { {
	// Components cannot be their own parts
	all c : Component | c.parts=c.parts-Component
  
} }
