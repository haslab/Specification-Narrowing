sig Track { succs : set Track, signals : set Signal } sig Junction, Entry, Exit in Track {} sig Signal {} sig Semaphore, Speed extends Signal {}
pred S0 { {
	// The station has at least one entry and one exit
	some Entry and some Exit
} }

pred S1 { {
	// The station has at least one entry and one exit
	
} }

pred S2 { {
	// The station has at least one entry and one exit
  	all t:Track | t in Entry and t in Exit
	
} }

pred S3 { {
	// The station has at least one entry and one exit
  	
  	
  	
  all t: Track | some e: Entry |some x: Exit |e in t.succs and x in t.succs 
	
} }
