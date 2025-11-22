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
