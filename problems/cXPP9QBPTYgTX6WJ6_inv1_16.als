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

pred S4 { {
	// The station has at least one entry and one exit
   
   
   some t: Track | t in Entry and t in Exit

	
} }

pred S5 { {
	// The station has at least one entry and one exit
  one Entry
  one Exit
	
} }

pred S6 { {
	// The station has at least one entry and one exit
  	all t : Track | some en : Entry, ex : Exit | en in t.*succs and ex in t.*succs
	
} }

pred S7 { {
	// The station has at least one entry and one exit
	lone Entry and lone Exit
} }

pred S8 { {
	// The station has at least one entry and one exit
	some Entry and one Exit
} }

pred S9 { {
  // The station has at least one entry and one exit
	all t: Track |
  		some en: Entry, e: Exit |
  			en in t.^succs and e in t.^succs
} }

pred S10 { {
	// The station has at least one entry and one exit
	some Entry
} }

pred S11 { {
	// The station has at least one entry and one exit
	all t : Track | some Entry and some Exit
} }

pred S12 { {
	// The station has at least one entry and one exit
	some entry: Entry | entry in Track.succs
  	some exit: Exit | exit in Track.succs
} }

pred S13 { {
	// The station has at least one entry and one exit
  	one t : Track | t in Entry and t in Exit
	
} }

pred S14 { {
	// The station has at least one entry and one exit
  	some t : Track | t in Entry or t in Exit
	
} }

pred S15 { {
	// The station has at least one entry and one exit
  all t : Track | some Exit & t.*succs and t in Entry.*succs  
	
} }
