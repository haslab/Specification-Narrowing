sig Room {}
one sig SecureLab extends Room {}
abstract sig Person { 
	owns : set Key 
}
sig Employee extends Person {}
sig Researcher extends Person {}
sig Key { 
	opens: one Room 
}
fact RoomsHaveKeys {
	all r : Room | some opens.r
}

pred Fix1 {
	all e : Employee | ( 
		(some k : Key | k in e.owns and SecureLab != k.opens)
		and
	 	e !in owns.opens.SecureLab
	)
}

pred Fix2 {
	all e : Employee | (
		all k : Key | k in e.owns implies SecureLab != k.opens
	)
}

pred Fix3 {
	all e : Employee | (
		no k : Key | k in e.owns
	)
}

pred Fix4 {
	all e : Employee | (
		some k : Key | k in e.owns and SecureLab != k.opens
	)
	Researcher = owns.opens.SecureLab
}


