sig Track { prox : set Track, signal : lone Signal } sig Junction extends Track {} sig Entry, Exit in Track {} sig Signal {} var sig Green in Signal {} sig Train { var pos : lone Track } fact Layout { all t : Track | t not in Junction iff (lone t.prox and lone prox.t) no t : Track | t in t.^prox all s : Signal | one signal.s all j : Junction, t : prox.j | some t.signal all t : Track | t in Entry iff no prox.t all t : Track | t in Exit iff no t.prox }
pred S0 { {
	// Signals are always alternating
  	always (all s:Signal | (s in Green implies eventually s not in Green) and (s not in Green implies eventually s in Green))
} }

pred S1 { {
	// Signals are always alternating
	always (all s : Signal | s in Green implies eventually s not in Green or 
  		   		s not in Green implies eventually s in Green)
} }

pred S2 { {
	// Signals are always alternating
	all s: Signal | always s != s'
} }

pred S3 { {
	// Signals are always alternating
	always Signal != Signal'
} }
