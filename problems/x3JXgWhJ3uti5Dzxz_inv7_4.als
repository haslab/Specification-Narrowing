sig User { follows : set User, sees : set Photo, posts : set Photo, suggested : set User } sig Influencer extends User {} sig Photo { date : one Day } sig Ad extends Photo {} sig Day {}
pred S0 { {
	// Suggested are other users followed by followed users, but not yet followed.
  all u: User | u.suggested = (u.follows.follows - u.follows - u)
	
} }

pred S1 { {
	// Suggested are other users followed by followed users, but not yet followed.
	all u : User | u.suggested in u.follows.follows - u.follows - u
} }

pred S2 { {
	// Suggested are other users followed by followed users, but not yet followed.
  all u: User | u.suggested = u.follows.follows - u.follows
	
} }

pred S3 { {
	// Suggested are other users followed by followed users, but not yet followed.
	all u : User | u.suggested in u.follows.follows - u.follows
} }
