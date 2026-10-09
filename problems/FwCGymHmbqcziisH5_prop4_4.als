sig Track { prox : set Track, signal : lone Signal } sig Junction extends Track {} sig Entry, Exit in Track {} sig Signal {} var sig Green in Signal {} sig Train { var pos : lone Track } fact Layout { all t : Track | t not in Junction iff (lone t.prox and lone prox.t) no t : Track | t in t.^prox all s : Signal | one signal.s all j : Junction, t : prox.j | some t.signal all t : Track | t in Entry iff no prox.t all t : Track | t in Exit iff no t.prox }
pred S0 { {
	// There are no collisions between trains
	all t : Train | always (lone pos.t)
} }

pred S1 { {
	// There are no collisions between trains
	all t1, t2 : Train | always t1.pos != t2.pos
} }

pred S2 { {
	// There are no collisions between trains
	all disj t1,t2:Train | no (t1.pos &t2.pos)
} }

pred S3 { {
	// There are no collisions between trains
	always (all disj t1,t2:Train | t1.pos != t2.pos)
} }
