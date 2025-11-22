sig User { follows : set User, sees : set Photo, posts : set Photo, suggested : set User } sig Influencer extends User {} sig Photo { date : one Day } sig Ad extends Photo {} sig Day {}
pred S0 { {
	// Users can see ads posted by everyone, 
	// but only see non ads posted by followed users.
  all u: User | u.sees in (u.follows.posts + Ad)
} }

pred S1 { {
	// Users can see ads posted by everyone, 
	// but only see non ads posted by followed users.
  	all u: User | u.sees = {Ad + u.follows.posts} 

} }

pred S2 { {
	// Users can see ads posted by everyone, 
	// but only see non ads posted by followed users.

} }

pred S3 { { 
	// Users can see ads posted by everyone, 
	// but only see non ads posted by followed users.
	
  	
  	all u: User | (u.follows.posts + Ad) in u.sees 
  	
} }
