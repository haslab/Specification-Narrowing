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

pred S4 { {
	// Every image is posted by one user.
  	all p: Photo, u: User | p in u.posts
	
} }

pred S5 { {
	// Every image is posted by one user.
  all x: Photo | one x.posts
	
} }

pred S6 { {
	// Every image is posted by one user.
	all p: Photo | one u: User | u.posts = p
} }

pred S7 { {
	// Every image is posted by one user.
  	one u : User | all p : Photo | p in u.posts
	
} }

pred S8 { {
  // Every image is posted by one user.
  all disj u1 : User, u2 : User | no (u1.posts & u2.posts)
} }

pred S9 { {
	// Every image is posted by one user.
  all u : User | lone u.posts
	
} }

pred S10 { {
	// Every image is posted by one user.
	all p : Photo | one User.posts
} }

pred S11 { {
	// Every image is posted by one user.
	all u : User | one posts.u
} }
