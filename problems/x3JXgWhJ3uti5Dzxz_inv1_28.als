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

pred S12 { {
	// Every image is posted by one user.
  	all p : Photo | lone User.posts
	
} }

pred S13 { {
	// Every image is posted by one user.
	one p: Photo, u: User | p in u.posts
} }

pred S14 { {
	// Every image is posted by one user.
  all x : Photo | some y : User | all z: User | y->x in posts	and y=z
} }

pred S15 { {
	// Every image is posted by one user.
  all u : User | one u.posts
	
} }

pred S16 { {
	// Every image is posted by one user.
  one (posts.Photo)
	
} }

pred S17 { {
  // Every image is posted by one user.
  all user: User | some photo: Photo | photo in user.posts
} }

pred S18 { {
	// Every image is posted by one user.
	
  	all p: Photo, u: User | one (p & u).posts
} }

pred S19 { {
	// Every image is posted by one user.
	all p: Photo | some u: User | u.posts = p
} }

pred S20 { {
	// Every image is posted by one user.
  all p : Photo | lone User
	
} }

pred S21 { {
	// Every image is posted by one user.
	lone posts.Photo
} }

pred S22 { {
	// Every image is posted by one user.
  one Photo.posts
  
	
} }

pred S23 { {
	// Every image is posted by one user.
  all p : Photo | one User
	
} }

pred S24 { {
	
	all u : User | u.posts not in u.sees
} }

pred S25 { {
	// Every image is posted by one user.
	all img : Photo, ad : Ad | img in User.posts and ad in User.posts
} }

pred S26 { {
	// Every image is posted by one user.
	all p:Photo , u:User| u.posts in p
} }

pred S27 { {
	// Every image is posted by one user.
  some p: Photo | one User.posts
	
} }
