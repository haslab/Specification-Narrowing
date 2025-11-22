sig User { follows : set User, sees : set Photo, posts : set Photo, suggested : set User } sig Influencer extends User {} sig Photo { date : one Day } sig Ad extends Photo {} sig Day {}
pred S0 { {
	// Every image is posted by one user.
  all p: Photo | one (posts.p)
	
} }

pred S1 { {
	// Every image is posted by one user.
	
} }

pred S2 { {
	// Every image is posted by one user.
  all p : Photo | some u : User | p in u.posts
	
} }

pred S3 { {
	// Every image is posted by one user.
	all x : Photo | lone posts.x
} }
