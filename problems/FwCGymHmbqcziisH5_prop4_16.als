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

pred S4 { {
	// There are no collisions between trains
	all t1,t2 : Train | always no (t1.pos & t2.pos)
} }

pred S5 { {
	// There are no collisions between trains
  always prox.~prox in iden
} }

pred S6 { {
	// There are no collisions between trains
	all disj s1, s2 : Signal | always s1.pos != s2.pos
} }

pred S7 { {
	// There are no collisions between trains
  always lone Train.pos
} }

pred S8 { {
	// There are no collisions between trains
  always ~prox.prox in iden
} }

pred S9 { {
	// There are no collisions between trains
  	always all t1, t2: Train | some tr1,tr2: Track | t1.pos in tr1 and t2.pos in tr1 implies t1=t2
} }

pred S10 { {
	// There are no collisions between trains
  all t: Train | always prox.~prox in iden
} }

pred S11 { {
	// There are no collisions between trains
  always lone pos.Track
} }

pred S12 { {
	// There are no collisions between trains
  always one pos.Track
} }

pred S13 { {
	// There are no collisions between trains
  	always all t1, t2: Train | some tr1: Track | always (t1.pos in tr1 and t2.pos in tr1 implies t1=t2)
} }

pred S14 { {
	// There are no collisions between trains
  	always all t1, t2: Train | lone tr1: Track | always (t1.pos in tr1 and t2.pos in tr1 implies t1=t2)
} }

pred S15 { {
	// There are no collisions between trains
  	always all t1, t2: Train | always lone tr1: Track | always (no t1.pos & t2.pos)
} }
