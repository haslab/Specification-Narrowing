sig Track { succs : set Track, signals : set Signal } sig Junction, Entry, Exit in Track {} sig Signal {} sig Semaphore, Speed extends Signal {}
pred S0 { {
	// Entry tracks must have a speed signal
  	all t:Entry | some (t.signals & Speed)  

} }

pred S1 { {
	// Entry tracks must have a speed signal
  	all e: Entry | Speed in e.signals

} }

pred S2 { {
	// Entry tracks must have a speed signal
  	all e: Entry | one s: Speed | s in e.signals 

} }

pred S3 { {
	// Entry tracks must have a speed signal
	all e : Entry | some e.signals
} }

pred S4 { {
	// Entry tracks must have a speed signal
  	all entry: Entry | entry.signals in Speed

} }

pred S5 { {
	// Entry tracks must have a speed signal
  	all t:Track | some (t.signals&Speed)  

} }

pred S6 { {
	// Entry tracks must have a speed signal


  all s:Speed, t:Track | t in Entry implies s in t.*succs

} }

pred S7 { {
	// Entry tracks must have a speed signal


  
  all t:Track, s: Signal| t in Entry implies t.signals in Signal
} }

pred S8 { {
	// Entry tracks must have a speed signal
	all e:Entry| some e.signals and e.signals in Speed 
} }

pred S9 { {
	// Entry tracks must have a speed signal
	some Entry.signals & Speed
} }

pred S10 { {
	// Entry tracks must have a speed signal
	all t:Track|all s:Signal| t in Entry => s in t.signals
} }

pred S11 { {
	// Entry tracks must have a speed signal


  
  all s: Signal, t:Track | t in Entry implies signals.s in Speed

} }
