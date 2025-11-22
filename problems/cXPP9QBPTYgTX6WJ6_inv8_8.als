sig Track { succs : set Track, signals : set Signal } sig Junction, Entry, Exit in Track {} sig Signal {} sig Semaphore, Speed extends Signal {}
pred S0 { {
	// It should be possible to reach every exit from every entry
  	all ex: Exit | all en: Entry | ex in en.*succs

} }

pred S1 { {
	// It should be possible to reach every exit from every entry
  	all ex: Exit | all en: Entry | ex in en.^succs

} }

pred S2 { {
	// It should be possible to reach every exit from every entry
	Exit in Entry.*succs
} }

pred S3 { {
	// It should be possible to reach every exit from every entry
  	all en: Entry, ex: Exit | ex in en.succs

} }

pred S4 { {
	// It should be possible to reach every exit from every entry
  	all e:Entry | e in Exit or (all ex:Exit | ex in e.^(succs)) 

} }

pred S5 { {
	// It should be possible to reach every exit from every entry
  	Exit in Entry.^succs

} }

pred S6 { {
	// It should be possible to reach every exit from every entry
  all e : Entry | some (e.^(succs) & Exit)

} }

pred S7 { {
	// It should be possible to reach every exit from every entry
	all e: Exit, ent: Entry | ent in e.^succs
} }
