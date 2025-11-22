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
