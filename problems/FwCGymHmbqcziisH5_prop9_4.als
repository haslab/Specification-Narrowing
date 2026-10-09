sig Track { prox : set Track, signal : lone Signal } sig Junction extends Track {} sig Entry, Exit in Track {} sig Signal {} var sig Green in Signal {} sig Train { var pos : lone Track } fact Layout { all t : Track | t not in Junction iff (lone t.prox and lone prox.t) no t : Track | t in t.^prox all s : Signal | one signal.s all j : Junction, t : prox.j | some t.signal all t : Track | t in Entry iff no prox.t all t : Track | t in Exit iff no t.prox }
pred S0 { {
	// All trains will eventually enter the station in entry tracks
    all t : Train | no t.pos until (some t.pos & Entry)
} }

pred S1 { {
	// All trains will eventually enter the station in entry tracks
		always ( all t:Train | eventually t.pos in Entry)
} }

pred S2 { {
	// All trains will eventually enter the station in entry tracks
	 (all t:Train | eventually ( some t.pos and t.pos in Entry) )
} }

pred S3 { {
	// All trains will eventually enter the station in entry tracks
	always ( all t:Train | no t.pos implies eventually (t.pos in Entry) )
} }
