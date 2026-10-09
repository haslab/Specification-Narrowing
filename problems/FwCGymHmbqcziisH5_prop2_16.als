sig Track { prox : set Track, signal : lone Signal } sig Junction extends Track {} sig Entry, Exit in Track {} sig Signal {} var sig Green in Signal {} sig Train { var pos : lone Track } fact Layout { all t : Track | t not in Junction iff (lone t.prox and lone prox.t) no t : Track | t in t.^prox all s : Signal | one signal.s all j : Junction, t : prox.j | some t.signal all t : Track | t in Entry iff no prox.t all t : Track | t in Exit iff no t.prox }
pred S0 { {
	// Every signal will eventually become green
	all s:Signal | eventually s in Green
} }

pred S1 { {
	// Every signal will eventually become green
	eventually (all s:Signal | s in Green)
} }

pred S2 { {
	// Every signal will eventually become green
	always all s: Signal | eventually s in Green
} }

pred S3 { {
	// Every signal will eventually become green
	always all s: Signal | eventually s = Green
} }

pred S4 { {
	// Every signal will eventually become green
  always(eventually Green = Signal)
} }

pred S5 { {
	// Every signal will eventually become green
	eventually (Green in Signal)
} }

pred S6 { {
	// Every signal will eventually become green
	all g : Signal | eventually g = Green 
} }

pred S7 { {
	// Every signal will eventually become green
	eventually some Green&Signal
} }

pred S8 { {
	// Every signal will eventually become green
  always eventually some Green
} }

pred S9 { {
	// Every signal will eventually become green
	eventually (all t:Track | Green in t.signal)
} }

pred S10 { {
	// Every signal will eventually become green
	eventually (all t:Track | eventually Green in t.signal)
} }

pred S11 { {
	// Every signal will eventually become green
	eventually (all s:Signal | eventually Green in s)
} }

pred S12 { {
	// Every signal will eventually become green
	eventually (all s:Signal | Green in s)
} }

pred S13 { {
	// Every signal will eventually become green
	eventually(all t:Track | t.signal = Green)
} }

pred S14 { {
	// Every signal will eventually become green
	eventually(all t:Track | eventually t.signal = Green)
} }

pred S15 { {
	// Every signal will eventually become green
	always(all t:Track | eventually t.signal = Green)
} }
