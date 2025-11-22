sig User { follows : set User, sees : set Photo, posts : set Photo, suggested : set User } sig Influencer extends User {} sig Photo { date : one Day } sig Ad extends Photo {} sig Day {}
pred S0 { {
  // A user only sees ads from followed or suggested users.
  all u: User | (u.sees & Ad) in (u.follows.posts + u.suggested.posts)
} }

pred S1 { {
	// A user only sees ads from followed or suggested users.
  
} }

pred S2 { {
	// A user only sees ads from followed or suggested users.
	
  	all u : User |
  		all a : Ad |
  			a in u.sees iff
  				(some y : User | (y in u.follows + u.suggested) and a in y.posts)

} }

pred S3 { {
	// A user only sees ads from followed or suggested users.
  	all x:User | x.sees-(Photo-Ad) in x.follows + x.suggested

} }
