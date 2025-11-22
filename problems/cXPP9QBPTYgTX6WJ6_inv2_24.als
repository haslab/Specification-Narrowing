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

pred S12 { {
	// Signals belong to one track
  	all t1,t2 : Track, s : Signal | (s in t1.signals or s in t1.^succs.signals) implies (s not in t2.signals or s not in t2.^succs.signals)

} }

pred S13 { {
	// Signals belong to one track

	#signals.Signal = 0 or #signals.Signal = 1
	Signal in Track.signals

} }

pred S14 { {
	// Signals belong to one track
	one(signals.Track)
} }

pred S15 { {
	// Signals belong to one track
	all s:Signal, t:Track | s -> t in signals
} }

pred S16 { {
	// Signals belong to one track

#signals.Signal =1
  Signal in Track.signals

} }

pred S17 { {
	// Signals belong to one track
	one t : Track | all s : Signal | s in t
} }

pred S18 { {
	// Signals belong to one track
	some t : Track | all s : Signal | s in t.signals
} }

pred S19 { {
	// Signals belong to one track
  all t : Track | no (t.signals & t.succs.signals)
} }

pred S20 { {
	// Signals belong to one track
  	no {s: Signal | #signals.s = 2}

} }

pred S21 { {
	// Signals belong to one track
  all t : Track | lone sem : Semaphore, speed : Speed | sem in t.signals and speed in t.signals
  

} }

pred S22 { {
	// Signals belong to one track
  	one signals.iden

} }

pred S23 { {
	// Signals belong to one track
	all t: Track | t.^signals not in t.^succs.signals 
} }
