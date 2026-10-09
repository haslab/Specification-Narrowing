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

pred S4 { {
	// All trains will eventually enter the station in entry tracks
   (all t:Train| eventually (no t.pos and after one t.pos:>Entry))
	 // all t:Train | some t.pos and (t.pos not in Entry implies before no t.pos and eventually ( some t.pos & Entry)   )
} }

pred S5 { {
	// All trains will eventually enter the station in entry tracks
  always (all t:Train| eventually (no t.pos and one t.pos':>Entry))
	 // all t:Train | some t.pos and (t.pos not in Entry implies before no t.pos and eventually ( some t.pos & Entry)   )
} }

pred S6 { {
	// All trains will eventually enter the station in entry tracks
	eventually (all t:Train | t.pos in Entry)	
} }

pred S7 { {
	// All trains will eventually enter the station in entry tracks
  always (all t:Train| eventually ( one t.pos':>Entry))
	 // all t:Train | some t.pos and (t.pos not in Entry implies before no t.pos and eventually ( some t.pos & Entry)   )
} }

pred S8 { {
	// All trains will eventually enter the station in entry tracks
	all t:Train | eventually t.pos in Entry
} }

pred S9 { {
	// All trains will eventually enter the station in entry tracks
		always ( all t:Train |some t.pos and eventually (t.pos in Entry))
} }

pred S10 { {
	// All trains will eventually enter the station in entry tracks
	 ( all t:Train |no t.pos implies  eventually ( some t.pos and t.pos in Entry) )
} }

pred S11 { {
	// All trains will eventually enter the station in entry tracks
	all t:Train | some t.pos and eventually t.pos in Entry
} }

pred S12 { {
	// All trains will eventually enter the station in entry tracks
	all t : Train | eventually t.pos = Entry
} }

pred S13 { {
	// All trains will eventually enter the station in entry tracks
	always ( all t:Train | (no t.pos) until (some t.pos :> Entry) )	
} }

pred S14 { {
	// All trains will eventually enter the station in entry tracks
	always ( all t:Train | some tk:Entry | eventually (no t.pos until t.pos in tk))
} }

pred S15 { {
	// All trains will eventually enter the station in entry tracks
 always eventually Train.pos in Entry
		//always ( all t:Train |(no prox.t) and after (t.pos in Entry) )
} }
