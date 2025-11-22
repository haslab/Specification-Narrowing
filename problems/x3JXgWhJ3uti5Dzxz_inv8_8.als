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

pred S4 { {
	// A user only sees ads from followed or suggested users.
	all u : User | u.sees in Ad & ( u.follows.posts + u.suggested.posts)
} }

pred S5 { {
      all u: User, p: Photo | (p in u.sees) implies ((p in Ad) or (p in u.follows.posts) or (p in u.suggested.posts))
} }

pred S6 { {
	// A user only sees ads from followed or suggested users.
	all u: User | u.sees = ((u.follows.posts + u.suggested.posts) & Ad)
} }

pred S7 { {
	// A user only sees ads from followed or suggested users.
  all u : User | u.sees = u.follows.posts + u.suggested.posts
} }
