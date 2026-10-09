sig Track { prox : set Track, signal : lone Signal } sig Junction extends Track {} sig Entry, Exit in Track {} sig Signal {} var sig Green in Signal {} sig Train { var pos : lone Track } fact Layout { all t : Track | t not in Junction iff (lone t.prox and lone prox.t) no t : Track | t in t.^prox all s : Signal | one signal.s all j : Junction, t : prox.j | some t.signal all t : Track | t in Entry iff no prox.t all t : Track | t in Exit iff no t.prox }
pred S0 { {
	// All trains inside the station will eventually leave the station
	always (all t:pos.Track | eventually no t.pos)
} }

pred S1 { {
	// All trains inside the station will eventually leave the station
	all t : Train | eventually always no t.pos
} }

pred S2 { {
	// All trains inside the station will eventually leave the station
	all t : Train | eventually no t.pos
} }

pred S3 { {
	// All trains inside the station will eventually leave the station
	all t:Train | some (t.pos & Entry ) implies eventually some (t.pos & Exit) 
} }

pred S4 { {
	// All trains inside the station will eventually leave the station
	always (all t:Train | some (t.pos & Entry ) implies eventually some (t.pos & Exit) )
} }

pred S5 { {
	// All trains inside the station will eventually leave the station
	all t : Train | always (eventually t.pos not in Entry)
} }

pred S6 { {
	// All trains inside the station will eventually leave the station
	always (all t:pos.Train | eventually no t.pos)
} }

pred S7 { {
	// All trains inside the station will eventually leave the station
	always (all t:Train | always some (t.pos & Entry ) implies eventually some (t.pos & Exit) )
} }
