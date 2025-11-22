sig Workstation { workers : set Worker, succ : set Workstation } one sig begin, end in Workstation {} sig Worker {} sig Human, Robot extends Worker {} abstract sig Product { parts : set Product } sig Material extends Product {} sig Component extends Product { workstation : set Workstation } sig Dangerous in Product {}
pred S0 { {
	// Components built of dangerous parts are also dangerous
	all c: Component | some (c.parts & Dangerous) implies c in Dangerous
} }

pred S1 { {
	// Components built of dangerous parts are also dangerous
	all o: Component | (o.parts in Dangerous) implies (o in Dangerous)
} }

pred S2 { {
	// Components built of dangerous parts are also dangerous
	all o: Component | (o.^parts in Dangerous) implies (o in Dangerous)
} }

pred S3 { {
	// Components built of dangerous parts are also dangerous
  all c:Component| some p:Product | (p in Dangerous and p in c.parts) implies c in Dangerous

} }

pred S4 { {
	// Components built of dangerous parts are also dangerous
	all o: Component | (Dangerous in o.^parts) implies (o in Dangerous)
} }

pred S5 { {
	// Components built of dangerous parts are also dangerous
	all o: Component | (Dangerous in o.parts) implies (o in Dangerous)
} }

pred S6 { {
	// Components built of dangerous parts are also dangerous
  	all c: Component | some p: c.parts | p in Dangerous implies c in Dangerous

} }

pred S7 { {
	// Components built of dangerous parts are also dangerous
  all c:Component | Dangerous in c.^parts implies Dangerous in c 

} }

pred S8 { {
	// Components built of dangerous parts are also dangerous
	all c:Component | some e:c.^(parts)| e in Dangerous implies c in Dangerous } }

pred S9 { {
	// Components built of dangerous parts are also dangerous
  all c : Component, p : Product | c in p.parts and p in Dangerous implies c in Dangerous

} }

pred S10 { {
	// Components built of dangerous parts are also dangerous
  all c: Component | (c in Dangerous) implies (c.parts in Dangerous)

} }

pred S11 { {
	// Components built of dangerous parts are also dangerous
    all c : Component | Dangerous in c.parts implies Dangerous in c

} }
