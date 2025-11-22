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

pred S4 { {
	// Components cannot be their own parts
	all c: Component | c not in c.parts and c not in c.parts.parts
} }

pred S5 { {
	// Components cannot be their own parts

} }

pred S6 { {
	// Components cannot be their own parts
  	one c:Component | c not in c.parts

} }

pred S7 { {
	// Components cannot be their own parts
	all c: Component | no c.parts
  
} }

pred S8 { {
	// Components cannot be their own parts
  	all c : Product | c not in c.parts
  

} }

pred S9 { {
	// Components cannot be their own parts
	all c: Component | c.parts != c
} }

pred S10 { {
	// Components cannot be their own parts
  	all x,y,z: Component| (y in x.parts and z in y.parts ) implies x not in (z.parts) 

} }

pred S11 { {
	// Components cannot be their own parts
  
	
 Component not in Component.parts
} }
