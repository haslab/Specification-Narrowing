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
