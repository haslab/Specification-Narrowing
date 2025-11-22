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

pred S8 { {
	// The station has no cycles
  	no (Exit.succs & Entry)
	no (succs.Entry & Exit)

} }

pred S9 { {
	// The station has no cycles
  	Track in Track.^succs

} }

pred S10 { {
	// The station has no cycles
	all t: Track | one e: Entry | one ex: Exit | e in t.^succs and ex in t.^succs
} }

pred S11 { {
	// The station has no cycles
  	Track not in Track.^succs

} }

pred S12 { {
	// The station has no cycles
	all disj t1, t2 : Track | t1 not in t2.*succs iff t2 in t1.*succs 
} }

pred S13 { {
	// The station has no cycles
  	Track not in Track.*succs

} }

pred S14 { {
	// The station has no cycles
	all t : Exit | no t.succs
} }

pred S15 { {
	// The station has no cycles
	all ex : Exit | no e : Entry | e in ex.^succs
} }
