sig Track { succs : set Track, signals : set Signal } sig Junction, Entry, Exit in Track {} sig Signal {} sig Semaphore, Speed extends Signal {}
pred S0 { {
	// Exit tracks are those without successor
  	all t : Track | t in Exit iff no t.succs

} }

pred S1 { {
  // Exit tracks are those without successor
  all e: Exit | no e.succs

} }

pred S2 { {
	// Exit tracks are those without successor
	all t : Track | no t.succs implies t in Exit
} }

pred S3 { {
	// Exit tracks are those without successor
	all e: Exit | no e.*succs
} }

pred S4 { {
	// Exit tracks are those without successor

} }

pred S5 { {
	// Exit tracks are those without successor
  	no succs.Exit

} }

pred S6 { {
	// Exit tracks are those without successor
  	all t : Track | some (Track - Exit).succs or lone Track
	no Exit.succs
} }

pred S7 { {
	// Exit tracks are those without successor
  all t : Track | no t.succs implies Exit in t 

} }

pred S8 { {
	// Exit tracks are those without successor
  all t : Track | no (t.succs-t) implies one (t & Exit)

} }

pred S9 { {
	// Exit tracks are those without successor
    all t: Track | no t.succs

} }

pred S10 { {
	// Exit tracks are those without successor
  all t : Track | Exit in t implies no t.succs

} }

pred S11 { {
	// Exit tracks are those without successor
	all t : Track | (t not in t.succs) and (no t.succs implies t in Exit)
} }
