sig Track { succs : set Track, signals : set Signal } sig Junction, Entry, Exit in Track {} sig Signal {} sig Semaphore, Speed extends Signal {}
pred S0 { {
	// Junctions are the tracks with more than one predecessor
	all t: Track | #(succs.t) > 1 <=> t in Junction
} }

pred S1 { {
	// Junctions are the tracks with more than one predecessor
	
  	all t: Junction | #succs.t > 1
} }

pred S2 { {
	// Junctions are the tracks with more than one predecessor
	all t: Junction | some succs.t
} }

pred S3 { {
    // Junctions are the tracks with more than one predecessor
      all t:Track | some succs.t iff t in Junction

} }

pred S4 { {
	// Junctions are the tracks with more than one predecessor
	all t: Track | #(succs.t) > 1 => t in Junction
} }

pred S5 { {
	// Junctions are the tracks with more than one predecessor
	all t: Junction | #(t.succs) > 1
} }

pred S6 { {
	// Junctions are the tracks with more than one predecessor

} }

pred S7 { {
	// Junctions are the tracks with more than one predecessor
  	all t: Track | t in Junction => some t2: Track | t in (t2.succs - t) and some t3: (t2.succs - t) | t in (t3.succs - t)
} }

pred S8 { {
	// Junctions are the tracks with more than one predecessor
	all t: Track | some t2: Track | some t3: Track | t in Junction iff t in t2.^succs and t2 != t3 and t in t3.^succs
} }

pred S9 { {
	// Junctions are the tracks with more than one predecessor
    all t: Track | #(~succs.t) > 1 <=> t in Junction

} }

pred S10 { {
	// Junctions are the tracks with more than one predecessor
	all j: Junction | some t: Track | j in t.succs.succs
} }

pred S11 { {
	// Junctions are the tracks with more than one predecessor
  
  
  all j: Junction | some s1,s2:Track -j  | j in s1.succs and j in s2.succs and not (s1=s2)

} }

pred S12 { {
	// Junctions are the tracks with more than one predecessor
  all j : Junction | some succs.j - j

} }

pred S13 { {
	// Junctions are the tracks with more than one predecessor
	all t : Track | t in Junction <=> some (Track.^succs - t)
} }

pred S14 { {
	// Junctions are the tracks with more than one predecessor
	all j: Junction | #(succs.j) > 1 and no j & succs.j
} }

pred S15 { {
	// Junctions are the tracks with more than one predecessor
	all t : Track | some t.succs implies t in Junction
} }
