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
