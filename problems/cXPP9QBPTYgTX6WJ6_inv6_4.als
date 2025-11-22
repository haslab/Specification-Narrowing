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
