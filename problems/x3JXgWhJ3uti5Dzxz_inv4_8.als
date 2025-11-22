sig User { follows : set User, sees : set Photo, posts : set Photo, suggested : set User } sig Influencer extends User {} sig Photo { date : one Day } sig Ad extends Photo {} sig Day {}
pred S0 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
  all u: User | some u.posts & Ad implies u.posts in Ad

} }

pred S1 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
  

} }

pred S2 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
	all u : User | some ad : Ad | ad in u.posts implies u.posts in Ad 
} }

pred S3 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
	all u:User | some p:Photo | p in Ad and p in u.posts implies u.posts in Ad
} }

pred S4 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
  all u : User | u.posts in Ad
} }

pred S5 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
  	
  	all u:User | Ad in u.posts implies u.posts in Ad

} }

pred S6 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
	

	
	
  	
	all u : User | some a : u.posts | a in Ad implies u.posts in Ad

} }

pred S7 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
	all u: User | all p: u.posts | p in Ad <=> u in p.posts
} }
