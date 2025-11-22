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

pred S12 { {
	// Components cannot be their own parts
	all c : Component | c.parts not in c
} }

pred S13 { {
	// Components cannot be their own parts
	some c:Component | c not in parts.c
} }

pred S14 { {
	// Components cannot be their own parts
  	all c : Component | c not in c.parts
  	all a,b : Component | a in b.parts implies b not in a.parts
  

} }

pred S15 { {
	// Components cannot be their own parts
	all c : Component | c.parts not in Component
} }

pred S16 { {
	// Components cannot be their own parts
  	no c: Component | no p: Product | p in c.parts and p = c

} }

pred S17 { {
	// Components cannot be their own parts
  all c:Component | some c.parts
	all c:Component | c not in c.parts
} }

pred S18 { {
	// Components cannot be their own parts
  	all c : Component | c not in Product.parts

} }

pred S19 { {
	// Components cannot be their own parts
	all p: Product | no p.*parts
} }

pred S20 { {
	// Components cannot be their own parts
  all c:Component | all p: c.parts | c not in p iff p not in parts.c
	
  
 
} }

pred S21 { {
	// Components cannot be their own parts
	all c: Component, d: Dangerous | c not in Component and d not in Dangerous
} }

pred S22 { {
	// Components cannot be their own parts
	all p : Product | (no p.parts & p) implies p in Component 
} }

pred S23 { {
	// Components cannot be their own parts
no disj c, p: Component | c in p.parts
} }

pred S24 { {
	// Components cannot be their own parts
	all c : Product | not c->c in parts
	all c1,c2 : Product | (c1!=c2 and c1->c2 in parts) implies not c2->c1 in parts
} }

pred S25 { {
	// Components cannot be their own parts
	all c: Component | 
  		some c2: Component |  c not in c2.parts
} }

pred S26 { {
	// Components cannot be their own parts
	Component.parts not in Component
} }

pred S27 { {
	// Components cannot be their own parts
  	all c : Component | Component not in c.parts

} }
