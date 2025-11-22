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

pred S8 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
	all u: User | some(u.posts & Ad) implies (u.posts = Ad)
} }

pred S9 { {
	// If a user posts an ad then all its posts should be labeled as ads.
  	all u : User | (one u.posts & Ad) implies u.posts in Ad

} }

pred S10 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
	all u:User | one up: u.posts | up in Ad implies u.posts in Ad
} }

pred S11 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
	all x: User | (some y: Photo | x->y in posts and y in Ad) implies 
  all z: Photo | x->z in posts and z in Ad  
} }

pred S12 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
  	all x: User | some y: Ad | y in x.posts implies (all z: Photo | z in x.posts and z in Ad) 
} }

pred S13 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
	all u : User, p : u.posts | Ad in p implies p = Ad
} }

pred S14 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
	all u : User, p : Photo | p in Ad implies u.posts in Ad
} }

pred S15 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
	all u : User | some pa : u.posts & Ad | #pa > 0 implies (all p : u.posts | p in Ad)
} }

pred S16 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
	all u: User | u.posts in Ad implies (u.posts not in Ad)
} }

pred S17 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
	all user: User | one post: Photo | post in user.posts and post in Ad => user.posts in Ad
} }

pred S18 { {
	// If a user posts an ad then all its posts should be labeled as ads.
  all u:User | Ad in u.posts implies (Photo not in u.posts)

} }

pred S19 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
	all user: User | one ad: Ad | ad in user.posts => user.posts in Ad
} }

pred S20 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
  	all u: User| all a: Ad |a in u.posts implies all p: u.posts| p in a
  
        

} }

pred S21 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
	all u : User | some p : u.posts | p in Ad  
  	
  	

} }

pred S22 { {
	// If a user posts an ad then all its posts should be labeled as ads.
  	all u:User | (Ad!=none and Ad in u.posts) implies (u.posts in Ad)
} }

pred S23 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
	all u: User | one p: Photo | ((p in Ad and p in u.posts) and u.posts in Ad)
} }

pred S24 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
	all u : User, p : u.posts | Ad in p implies u.posts = Ad
} }

pred S25 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
  	all u :User, p: Photo | some y: Ad | y in u.posts implies( p in u.posts implies p in Ad)
} }

pred S26 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
  	all u: User, a: Ad | a in u.posts implies (all p: Photo | p in Ad)

} }

pred S27 { {
	// If a user posts an ad then all its posts should be labeled as ads. 
  all x : User | all y : Photo | (x in posts.y) and (y in Ad) 
} }
