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

pred S16 { {
	// Users cannot follow themselves.
	User not in User.follows
} }

pred S17 { {
	// Users cannot follow themselves.
    all user : User | user not in user.suggested
} }

pred S18 { {
	// Users cannot follow themselves.
  all u:User , other:User-u |
  	other in u.follows

} }

pred S19 { {
	// Users cannot follow themselves.
  	all x,y : User | x->y in follows implies y->x not in follows
} }

pred S20 { {
	// Users cannot follow themselves.
  	follows in iden

} }

pred S21 { {
	// Users cannot follow themselves.
    
  	
  
	
  
	no User.follows & follows.User
} }

pred S22 { {
	// Users cannot follow themselves.
	one u1: User | one u2: User | u1 -> u2 in follows
  
} }

pred S23 { {
	// Users cannot follow themselves.
  
  all p1, p2 : User | p1.follows = p2 

} }

pred S24 { {
	// Users cannot follow themselves.
	all x, y : User | some follows.x
} }

pred S25 { {
	// Users cannot follow themselves.
	all u : User | one follows.u 
} }

pred S26 { {
	// Users cannot follow themselves.
	all disj u0,u1 : User | no (u0.^follows & u1.^follows)
} }

pred S27 { {
	// Users cannot follow themselves.
	all disj u0,u1 : User | one (u0.^follows & u1.^follows)
} }
