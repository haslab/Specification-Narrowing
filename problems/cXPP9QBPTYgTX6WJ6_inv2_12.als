sig Track { succs : set Track, signals : set Signal } sig Junction, Entry, Exit in Track {} sig Signal {} sig Semaphore, Speed extends Signal {}
pred S0 { {
	// Signals belong to one track
  all s: Signal | one t: Track | s in t.signals
} }

pred S1 { {
	// Signals belong to one track
	all t1, t2 : Track | all s : Signal | s in t1.signals and s in t2.signals implies t1=t2
} }

pred S2 { {
	// Signals belong to one track
	all s : Signal | s in Track.signals
} }

pred S3 { {
	// Signals belong to one track
  	no disj t1, t2: Track | t1.signals in t2. signals

} }

pred S4 { {
	// Signals belong to one track
	all s : Signal | one t : Track | s in t
} }

pred S5 { {
	// Signals belong to one track

} }

pred S6 { {
	// Signals belong to one track
		one t: Track | all s:Signal | s in t.signals 

} }

pred S7 { {
	// Signals belong to one track
	one(signals.Signal)
} }

pred S8 { {
	// Signals belong to one track
	all t : Track | all s : Signal | s in t.signals
} }

pred S9 { {
	// Signals belong to one track
	all t: Track | one signals.t
} }

pred S10 { {
	// Signals belong to one track
  all t: Track | one t.signals

} }

pred S11 { {
	// Signals belong to one track
  	all t1, t2 : Track | no (t1.signals & t2.signals)
} }
