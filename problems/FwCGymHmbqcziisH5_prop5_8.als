sig Track { prox : set Track, signal : lone Signal } sig Junction extends Track {} sig Entry, Exit in Track {} sig Signal {} var sig Green in Signal {} sig Train { var pos : lone Track } fact Layout { all t : Track | t not in Junction iff (lone t.prox and lone prox.t) no t : Track | t in t.^prox all s : Signal | one signal.s all j : Junction, t : prox.j | some t.signal all t : Track | t in Entry iff no prox.t all t : Track | t in Exit iff no t.prox }
pred S0 { {
	// A train inside the station can only move to one of the next tracks (or exit the station if it is in an exit track)
	always (all t:Train | some t.pos implies (t.pos' = t.pos or some t.pos' & t.pos.prox or (some t.pos & Exit and no t.pos')))
} }

pred S1 { {
	// A train inside the station can only move to one of the next tracks (or exit the station if it is in an exit track)
	//always all t:Train |t.pos in Entry  implies some t.pos.prox in  
} }

pred S2 { {
	// A train inside the station can only move to one of the next tracks (or exit the station if it is in an exit track)

    all t:Train |{
     	always (t.pos in Exit implies no t.pos')
      	always (t.pos in Track-Exit  implies  (t.pos'in  (t.pos.prox) )) 
    }
  	
} }

pred S3 { {
	// A train inside the station can only move to one of the next tracks (or exit the station if it is in an exit track)

    all t:Train |{
     	always (t.pos in Exit implies  no t.pos')
      	//always (t.pos in Entry  implies  (t.pos'in  (t.pos.prox) )) 
    }
  	
} }

pred S4 { {
	// A train inside the station can only move to one of the next tracks (or exit the station if it is in an exit track)
	always (all t:Train |t.pos in Entry  implies  (t.pos'in  t.pos.^prox)   or  t.pos in Exit implies no t.pos')
} }

pred S5 { {
	// A train inside the station can only move to one of the next tracks (or exit the station if it is in an exit track)

    all t:Train |{
     	always (t.pos in Exit implies  t.pos'= t.pos)
      	//always (t.pos in Entry  implies  (t.pos'in  (t.pos.prox) )) 
    }
  	
} }

pred S6 { {
	// A train inside the station can only move to one of the next tracks (or exit the station if it is in an exit track)
  
  always (all t:Train|(one t.pos:> Exit => no t.pos'))
 always (all t:Train| (one t.pos and some t.pos.prox  => t.pos' in t.pos.prox ) )
 always (all t:Train| (no t.pos.prox and one t.pos:> Track-Exit)  => (no t.pos' or t.pos'=t.pos) )
  
  
 /* all t:Train| {
	always (t.pos in Exit  implies eventually no t.pos)
    always (t.pos in (Track-Exit)  implies  t.pos' in t.pos.prox)
  }*/
} }

pred S7 { {
	// A train inside the station can only move to one of the next tracks (or exit the station if it is in an exit track)
  	always all t : Train {
  		(t.pos = Exit) implies no t.pos'
      	or
      	(one t.pos) implies (t.pos' in t.pos.prox)
  	}
} }
