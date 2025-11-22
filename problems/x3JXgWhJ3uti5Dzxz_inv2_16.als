sig User { follows : set User, sees : set Photo, posts : set Photo, suggested : set User } sig Influencer extends User {} sig Photo { date : one Day } sig Ad extends Photo {} sig Day {}
pred S0 { {
	// Users cannot follow themselves.
    all u: User | u not in u.follows
} }

pred S1 { {
	// Users cannot follow themselves.

} }

pred S2 { {
	// Users cannot follow themselves.
  all u: User | no follows.u

} }

pred S3 { {
	// Users cannot follow themselves.
  all x : User | x & iden.x in none

} }

pred S4 { {
	// Users cannot follow themselves.
  	all u : User |  (u in u.follows)

} }

pred S5 { {
	// Users cannot follow themselves.
	all u: User | u not in u.^follows
} }

pred S6 { {
	// Users cannot follow themselves.
  	all u: User | u.follows != u

} }

pred S7 { {
	// Users cannot follow themselves.
  one u:User | u not in u.follows
  

} }

pred S8 { {
	// Users cannot follow themselves.

  	

	
	// 
  	

	
	
	//
  	
  
  all x, y: User | not(x->y in follows) and x = y
} }

pred S9 { {
	// Users cannot follow themselves.
	follows not in iden
} }

pred S10 { {
	// Users cannot follow themselves.
	all disj u0,u1 : User | no (u0.follows & u0.follows) 
 	
} }

pred S11 { {
	// Users cannot follow themselves.
  	follows.~follows in iden
} }

pred S12 { {
	// Users cannot follow themselves.
  	all u : User |  u.*(follows) != u

} }

pred S13 { {
	// Users cannot follow themselves.
	all disj u0,u1 : User | no (u0.follows - u1.follows)
} }

pred S14 { {
	// Users cannot follow themselves.
  	not follows in ~follows

} }

pred S15 { {
	// Users cannot follow themselves.
  all u : User | some u1 : User | u1 in u.follows implies u!=u1

} }
