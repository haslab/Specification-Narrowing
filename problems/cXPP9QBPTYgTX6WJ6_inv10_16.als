sig Track { succs : set Track, signals : set Signal } sig Junction, Entry, Exit in Track {} sig Signal {} sig Semaphore, Speed extends Signal {}
pred S0 { {
	// Every track before a junction has a semaphore
  	all t: Track | some (Junction&t.succs) implies some (Semaphore&t.signals)

} }

pred S1 { {
	// Every track before a junction has a semaphore
  	all t : Track | some(succs.t & Junction) implies some(t.signals & Semaphore)
  

} }

pred S2 { {
	// Every track before a junction has a semaphore
	all t: Track, j: Junction {
      j in t.succs => Semaphore in t.signals
    }
} }

pred S3 { {
	// Every track before a junction has a semaphore
	some succs.Junction.signals & Semaphore
} }

pred S4 { {
	// Every track before a junction has a semaphore
	all t : Track | some(t.succs & Junction) implies one(t.signals & Semaphore)
} }

pred S5 { {
	// Every track before a junction has a semaphore
	all t: Track | (t.succs in Junction) => some (t.signals&Semaphore)
} }

pred S6 { {
	// Every track before a junction has a semaphore
  	all t: Track | some s: Semaphore | t.succs in Junction implies s in t.signals

} }

pred S7 { {
	// Every track before a junction has a semaphore

} }

pred S8 { {
	// Every track before a junction has a semaphore

  
  
  all x: Junction | not (Semaphore & succs.x.signals = none)

} }

pred S9 { {
	// Every track before a junction has a semaphore
	all t: Track | some j: Junction | j in t.succs => some s: Semaphore | s in t.signals
} }

pred S10 { {
	// Every track before a junction has a semaphore
	all t: (Junction.succs) | Semaphore in t.signals
} }

pred S11 { {
	// Every track before a junction has a semaphore
	all t: Track | some j: Junction, s: Semaphore | (j in t.succs) implies (s in t.signals)
} }

pred S12 { {
	// Every track before a junction has a semaphore
	all t : Track | Junction in t.succs implies Semaphore in t.signals
} }

pred S13 { {
	// Every track before a junction has a semaphore
  
  all j : Junction | succs.j.signals in Semaphore

} }

pred S14 { {
	// Every track before a junction has a semaphore
	all t: Track | Junction in t.succs iff Semaphore in t.signals
} }

pred S15 { {
	// Every track before a junction has a semaphore
	all t: Track | succs.t in Junction => some t.signals&Semaphore
} }
