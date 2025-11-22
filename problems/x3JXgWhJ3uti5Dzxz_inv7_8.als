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

pred S4 { {
	// Suggested are other users followed by followed users, but not yet followed.
    all u:User | (u.follows.follows - u.follows - u) in u.suggested
} }

pred S5 { {
	// Suggested are other users followed by followed users, but not yet followed.
  	all u1: User, u2: User, u3:User |u1 in u3.suggested implies u1 in u2.follows and  u2 in u3.follows and u1 not in u3.follows
	
} }

pred S6 { {
	// Suggested are other users followed by followed users, but not yet followed.
	
  
} }

pred S7 { {
	// Suggested are other users followed by followed users, but not yet followed.
    all u:User |  (u.follows.follows - u.follows) in u.suggested
} }
