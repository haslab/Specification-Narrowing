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

pred S8 { {
	// Components must have parts and materials have no parts
	all p : Product | p in Component and some p.parts
  	all m : Product | m in Material and no m.parts
} }

pred S9 { {
	// Components must have parts and materials have no parts
	all m:Material |
  		m.parts not in Product.parts
  
  	all c:Component |
  		some p:Product.parts |
  			p in c.parts
} }

pred S10 { {
	// Components must have parts and materials have no parts
  	all c: Component | c.parts in Product and no m: Material | m.parts in Product


} }

pred S11 { {
	// Components must have parts and materials have no parts
  
	
  	
  	all c: Component | c.parts in (Product - c)
  	all m:Material | m.parts not in (Product)
  	
} }

pred S12 { {
	// Components must have parts and materials have no parts
	all c: Component, m:Material | some p:Product | p in c.parts and p not in m.parts
} }

pred S13 { {
	// Components must have parts and materials have no parts
	all c: Component | c.parts != none and all m: Material | no parts.m
} }

pred S14 { {
	// Components must have parts and materials have no parts
	all p:Product | p.parts in (Component-Material)

} }

pred S15 { {
	// Components must have parts and materials have no parts
 	
  	all c: Component | c.*parts in (Product - c)
  	
} }

pred S16 { {
	// Components must have parts and materials have no parts
  all c : Component | some parts.c
  
  all m : Material | no parts.m

} }

pred S17 { {
	// Components must have parts and materials have no parts
		all c : Component , m : Material | some c.*parts and no m.parts 
  	
} }

pred S18 { {
	// Components must have parts and materials have no parts
  all c: Component, m: Material | #c.parts>0 and #m.parts =0 and c not in c.parts

} }

pred S19 { {
	// Components must have parts and materials have no parts
	all c : Component | some c.parts
	no Product.parts
} }

pred S20 { {
	// Components must have parts and materials have no parts
  	all c:Component | some p: Product | p in c.parts
  	all c:Material | some p: Product | p not in c.parts
} }

pred S21 { {
	// Components must have parts and materials have no parts
	all p : Product, m : Material, c : Component | p in c.parts and p not in m.parts
} }

pred S22 { {
	// Components must have parts and materials have no parts
  	no (iden & parts) and parts in (Component -> some Product)

} }

pred S23 { {
	// Components must have parts and materials have no parts
	all p : Product | parts.p = Component
} }

pred S24 { {
	// Components must have parts and materials have no parts
	all c: Component, p: Product | c in p.parts
  	 all m: Material, p: Product | not m in p.parts
} }

pred S25 { {
	// Components must have parts and materials have no parts
	
  	 
  
  	all c: Component, p: Product | c in p implies c in p.parts
  	 all m: Material, p: Product | m in p implies m not in p.parts
} }

pred S26 { {
	// Components must have parts and materials have no parts
	some (Product & Component - Dangerous).parts and no (Product & Material - Dangerous).parts 
} }

pred S27 { {
	// Components must have parts and materials have no parts
	all c : Component, m : Material | some p : Product | p in parts.c and p not in parts.m
} }
