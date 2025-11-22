sig Track { succs : set Track, signals : set Signal } sig Junction, Entry, Exit in Track {} sig Signal {} sig Semaphore, Speed extends Signal {}
pred S0 { {
	// Entry tracks are those without predecessors
	all t : Track | no succs.t iff t in Entry
} }

pred S1 { {
  // Entry tracks are those without predecessors
  all e: Entry | no succs.e
} }

pred S2 { {
	// Entry tracks are those without predecessors
all t: Entry | no t.^succs
} }

pred S3 { {
	// Entry tracks are those without predecessors
	all t:Track | no succs.t implies t in Entry 
} }

pred S4 { {
	// Entry tracks are those without predecessors
	all t1,t2 :Track | t1 in Entry iff t1 not in t2.succs 
} }

pred S5 { {
	// Entry tracks are those without predecessors
all t: Entry | no t.*succs
} }

pred S6 { {
	// Entry tracks are those without predecessors

} }

pred S7 { {
	// Entry tracks are those without predecessors
  	all t: Track, t2: Track | t in Entry iff t != t2 and t not in t2.^succs

} }

pred S8 { {
	// Entry tracks are those without predecessors
  	all t: Track, t2: Track | t in Entry iff t not in t2.^succs

} }

pred S9 { {
	// Entry tracks are those without predecessors
  all t: Track | t in Entry iff no t.succs
  

} }

pred S10 { {
	// Entry tracks are those without predecessors
  	all t: Track, t2: Track | t in Entry iff t not in t.^succs and t not in t2.^succs

} }

pred S11 { {
	// Entry tracks are those without predecessors
  	all t: Track, t2: Track - t | t in Entry iff t not in t2.^succs

} }

pred S12 { {
	// Entry tracks are those without predecessors
	all e : Entry , t:Track - e| e not in t.*succs
} }

pred S13 { {
	// Entry tracks are those without predecessors
  all t: Track, r: Track - t | t not in r.succs <=> t in Entry

} }

pred S14 { {
	// Entry tracks are those without predecessors
  	all t : Track | all t1 : Track | t not in t1.succs => t in Entry
} }

pred S15 { {
	// Entry tracks are those without predecessors
  	all disj t1, t2: Track | t1 not in t2.succs => t1 in Entry
} }

pred S16 { {
	// Entry tracks are those without predecessors

  	all e: Entry | all t: Track | e not in t.succs
  	all t: Track - Exit | some t.succs

} }

pred S17 { {
	// Entry tracks are those without predecessors
  all t:Track | no t.succs implies t in Entry

} }

pred S18 { {
	
  	
  	
  	all t1: Track, t2: Track | t1 != t2 and t1 in Entry iff t1 not in {t2.succs+t1.succs}
  	
	
} }

pred S19 { {
	// Entry tracks are those without predecessors
	all t : Track | all t2 : Track-t | t in Entry implies (not t in Track.succs and not t in t2.succs)
} }
