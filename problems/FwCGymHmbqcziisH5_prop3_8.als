sig Track { prox : set Track, signal : lone Signal } sig Junction extends Track {} sig Entry, Exit in Track {} sig Signal {} var sig Green in Signal {} sig Train { var pos : lone Track } fact Layout { all t : Track | t not in Junction iff (lone t.prox and lone prox.t) no t : Track | t in t.^prox all s : Signal | one signal.s all j : Junction, t : prox.j | some t.signal all t : Track | t in Entry iff no prox.t all t : Track | t in Exit iff no t.prox }
pred S0 { {
	// Trains never move
  // está horrível mas funciona
  //all t: Train, tk: Track | (t->tk in pos implies always t->tk in pos) and (t->tk not in pos implies always t->tk not in pos)
  always pos' = pos
} }

pred S1 { {
	// Trains never move
  // está horrível mas funciona
  //all t: Train, tk: Track | (t->tk in pos implies always t->tk in pos) and (t->tk not in pos implies always t->tk not in pos)
  always prox' = prox
} }

pred S2 { {
	// Trains never move
  always all t: Train, tk: Track | t->tk in pos implies always t->tk in pos
} }

pred S3 { {
	// Trains never move
		always no prox
} }

pred S4 { {
	// Trains never move
	always no Train.pos
} }

pred S5 { {
	// Trains never move
	always no Train
} }

pred S6 { {
	// Trains never move
	always Train.pos' =Train.pos
} }

pred S7 { {
	// Trains never move
	always all t: Train | one tr: Track | always t in pos.tr implies t' in pos.tr
} }
