sig Track { succs : set Track, signals : set Signal } sig Junction, Entry, Exit in Track {} sig Signal {} sig Semaphore, Speed extends Signal {}
pred S0 { {
	// Tracks not followed by junctions do not have semaphores
  	all t : Track | no (Junction&t.succs) implies no (Semaphore&t.signals)

} }

pred S1 { {
	// Tracks not followed by junctions do not have semaphores
  	all t : Track | Junction not in t.succs implies Semaphore not in t.signals

} }

pred S2 { {
	// Tracks not followed by junctions do not have semaphores
	all t : Track | t.succs not in Junction => no (Semaphore & t.signals)
} }

pred S3 { {
	// Tracks not followed by junctions do not have semaphores
	all t:Track|all j :Junction| j not in t.succs implies no s:Semaphore| s in t.signals
} }

pred S4 { {
	// Tracks not followed by junctions do not have semaphores
	all t : Track | t.succs not in Junction => t.signals not in Semaphore
} }

pred S5 { {
	// Tracks not followed by junctions do not have semaphores

} }

pred S6 { {
	// Tracks not followed by junctions do not have semaphores
  all t: Track | no Junction & t.^succs => no t.signals & Semaphore

} }

pred S7 { {
	// Tracks not followed by junctions do not have semaphores
	all t: Track | {
      Junction in t.succs => Semaphore in t.signals
      Junction not in t.succs => Semaphore not in t.signals
    }
} }

pred S8 { {
	// Tracks not followed by junctions do not have semaphores
  all t : Track | no (succs.t & Junction) implies no (Semaphore & t.signals)
  
  

} }

pred S9 { {
	// Tracks not followed by junctions do not have semaphores
	all t: Track, j: Junction|
  		j not in t.^succs implies (all s: t.signals | s not in Semaphore)
} }

pred S10 { {
	// Tracks not followed by junctions do not have semaphores
	all t: Track | t.^succs not in Junction implies t.signals not in Semaphore
} }

pred S11 { {
	// Tracks not followed by junctions do not have semaphores
  	
	
  all t : Track| t.succs != none and some(t.succs & Junction) implies no(t.signals & Semaphore)
} }

pred S12 { {
    // Tracks not followed by junctions do not have semaphores
    all t: Track - Junction | no t.signals & Semaphore
} }

pred S13 { {
	// Tracks not followed by junctions do not have semaphores
    all t: Track | no(t.succs & Junction) <=> no(t.signals & Semaphore)
} }

pred S14 { {
	// Tracks not followed by junctions do not have semaphores
	all t: Track, s: Semaphore | t.^succs not in Junction implies s not in t.signals
} }

pred S15 { {
	// Tracks not followed by junctions do not have semaphores
	all t: Track | Junction not in t.*succs => Semaphore not in t.signals
} }
