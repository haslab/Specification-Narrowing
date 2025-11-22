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
