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
