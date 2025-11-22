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

pred S8 { {
	// A user only sees ads from followed or suggested users.
  	all u: User | ((u.suggested + u.follows).posts & Ad) in u.sees

} }

pred S9 { {
    // A user only sees ads from followed or suggested users.
  	all u: User | all a: Ad | a in u.follows.posts or a in u.suggested.posts

} }

pred S10 { {
	// A user only sees ads from followed or suggested users.
  all u: User | (u.sees & Ad) in (u.follows.posts & u.suggested.posts)

} }

pred S11 { {
	// A user only sees ads from followed or suggested users.
  	all u : User | u.sees  & Ad = (u.follows.posts + u.suggested.posts) 

} }

pred S12 { {
	// A user only sees ads from followed or suggested users.
	all u: User | (posts.(u.sees & Ad) - u) in (u.follows + u.suggested)
} }

pred S13 { {
	// A user only sees ads from followed or suggested users.
	all u: User, s: u.sees | all u1: u.follows, u2: u.suggested | (s in u1.posts) or (s in u2.posts)
} }

pred S14 { {
	// A user only sees ads from followed or suggested users.
	User.sees in Ad
} }

pred S15 { {
	// A user only sees ads from followed or suggested users.
  










     all a : Ad | posts.a in sees.a.(follows+suggested)
} }

pred S16 { {
	// A user only sees ads from followed or suggested users.
  	all u: User | all p: u.posts | p not in u.sees
  	all u: User | ((u.suggested + u.follows).posts & Ad) in u.sees

} }

pred S17 { {
	// A user only sees ads from followed or suggested users.
  all u: User, a: Ad | some f: u.follows| some s: u.suggested| a in u.sees implies (a in f.posts or a in s.posts)

} }

pred S18 { {
	// A user only sees ads from followed or suggested users.
  all u: User, a: Ad | all f: u.follows| all s: u.suggested| a in u.sees implies (a in f.posts or a in s.posts)

} }

pred S19 { {
	// A user only sees ads from followed or suggested users.
  all u : User | (u.follows.posts + u.suggested.posts) in Ad
} }

pred S20 { {
	// A user only sees ads from followed or suggested users.
	all u : User | all a : Ad | (a in u.sees) implies (a in u.follows.posts or a in u.suggested)

} }

pred S21 { {
	// A user only sees ads from followed or suggested users.
  all a: Ad, x, y: User | x->a in sees implies (y->a in posts and (y in x.follows or y in x.suggested))
} }

pred S22 { {
	// A user only sees ads from followed or suggested users.
	all u: User, seg: u.follows | u != seg implies Ad in seg.sees or Ad in u.suggested
} }

pred S23 { {
	// A user only sees ads from followed or suggested users.
  all u : User | u.sees = u.follows.posts + u.suggested.posts & Ad

} }

pred S24 { {
	// A user only sees ads from followed or suggested users.
    all u: User, su: User |
        su in u.suggested =>
            su not in u.follows and
            some f: u.follows | su in f.follows


} }

pred S25 { {
	// A user only sees ads from followed or suggested users.
	all u1:User, p:Photo | u1.sees in Ad implies posts.p in u1.follows or posts.p in u1.suggested
} }

pred S26 { {
	// A user only sees ads from followed or suggested users.
  all x : User, y : Photo | x->y in sees and y in Ad implies some z: User | x->z in follows or x->z in suggested
  } }

pred S27 { {
	// A user only sees ads from followed or suggested users.
  all u : User | (u.follows.posts & u.suggested.posts) in Ad
} }
