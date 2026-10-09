sig Track { prox : set Track, signal : lone Signal } sig Junction extends Track {} sig Entry, Exit in Track {} sig Signal {} var sig Green in Signal {} sig Train { var pos : lone Track } fact Layout { all t : Track | t not in Junction iff (lone t.prox and lone prox.t) no t : Track | t in t.^prox all s : Signal | one signal.s all j : Junction, t : prox.j | some t.signal all t : Track | t in Entry iff no prox.t all t : Track | t in Exit iff no t.prox }
pred S0 { {
	// Trains cannot remain forever stopped in same position
    always all t : Train | some t.pos implies eventually t.pos != t.pos'
} }

pred S1 { {
	// Trains cannot remain forever stopped in same position
	always eventually (some t:Train | (t.pos)' != t.pos)
} }

pred S2 { {
	// Trains cannot remain forever stopped in same position
	all t : Train | (some t.pos) implies (eventually t.pos != t.pos')
} }

pred S3 { {
	// Trains cannot remain forever stopped in same position
	always (some t: Train| (no t.pos  implies eventually some t.pos) or t.pos != t.pos')
} }

pred S4 { {
	// Trains cannot remain forever stopped in same position
	always eventually (some Train implies (Train.pos)' != Train.pos)
} }

pred S5 { {
	// Trains cannot remain forever stopped in same position
	all t : Train | eventually t.pos != t.pos'
} }

pred S6 { {
	// Trains cannot remain forever stopped in same position
	eventually always (some t: Train| (no t.pos  implies some t.pos) or t.pos != t.pos')
} }

pred S7 { {
	// Trains cannot remain forever stopped in same position
	eventually always (pos != pos')
} }
