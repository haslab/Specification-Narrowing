sig Track { succs : set Track, signals : set Signal } sig Junction, Entry, Exit in Track {} sig Signal {} sig Semaphore, Speed extends Signal {}
pred S0 { {
	// The station has no cycles
	all t: Track | t not in t.^succs

} }

pred S1 { {
	// The station has no cycles
  	all t:Track | t not in t.*(succs) 

} }

pred S2 { {
	// The station has no cycles
  	all t:Track | t not in t.succs 

} }

pred S3 { {
	// The station has no cycles
	
} }

pred S4 { {
	// The station has no cycles
	all t1: Track, t2: Track | t2 not in t1.^succs
} }

pred S5 { {
	// The station has no cycles
	all t : Track | some t1:Track | t1 in t.succs => t not in t1.^succs
} }

pred S6 { {
	// The station has no cycles
	all t1, t2: Track | t1 in t2.succs implies (t1.succs.succs & t2.succs) = none
} }

pred S7 { {
	// The station has no cycles
  
  all t :  Track | not (t in Entry and t in Exit )

} }
