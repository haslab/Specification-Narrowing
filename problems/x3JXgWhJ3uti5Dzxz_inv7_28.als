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

pred S8 { {

  	// Suggested are other users followed by followed users, but not yet followed.
 
  
  
  
 
  
  
  all u1:User, u2:User-u1 |
  	u2 in u1.suggested implies ((u2 not in u1.follows) and u2 in (u1.follows.follows))
  
} }

pred S9 { {
	// Suggested are other users followed by followed users, but not yet followed.
	all u1,u2 : User | u1 != u2 and (u1 in u2.follows and u2 not in u1.follows => u2 in u1.suggested)
} }

pred S10 { {
	// Suggested are other users followed by followed users, but not yet followed.
  (all disj u, s: User|
  s in u.suggested iff s not in u.follows and s in (u.follows).follows)
	
} }

pred S11 { {
	// Suggested are other users followed by followed users, but not yet followed.
  all u : User | all s : u.suggested | all f:u.follows |
  		(u != s) and (s not in u.follows) and (s in f.follows)
  		
	
} }

pred S12 { {
	// Suggested are other users followed by followed users, but not yet followed.

  all u : User | u.suggested in u.follows.follows 
} }

pred S13 { {
	// Suggested are other users followed by followed users, but not yet followed.
  all u : User | u.suggested not in u.follows and u.suggested in u.follows.follows
	
} }

pred S14 { {
	// Suggested are other users followed by followed users, but not yet followed.
	all u: User | u.suggested in (u.follows.follows - u)
} }

pred S15 { {
	// Suggested are other users followed by followed users, but not yet followed.
	all u : User | all uf : u.follows | uf.follows in u.suggested
} }

pred S16 { {
	// Suggested are other users followed by followed users, but not yet followed.
  	all u:User | u.suggested = u.follows.follows
	
} }

pred S17 { {
	// Suggested are other users followed by followed users, but not yet followed.
  all u : User | u.suggested not in u.follows and u.suggested in (u.follows.follows - u)
	
} }

pred S18 { {
	// Suggested are other users followed by followed users, but not yet followed.
	all u: User | all s: u.suggested | all f: u.follows | s not in u.follows && s in f.follows
} }

pred S19 { {
	// Suggested are other users followed by followed users, but not yet followed.
	all x : User, y : User, z : User | z in x.follows and y in z.follows and x != y implies y in x.suggested
} }

pred S20 { {
	// Suggested are other users followed by followed users, but not yet followed.
	all disj u1: User, u2: User | all u3: u2.follows | ((u2 in u1.follows) and (u3 not in u1.follows)) implies u3 in u1.suggested
  	all u: User | u not in u.suggested
} }

pred S21 { {
  // Suggested are other users followed by followed users, but not yet followed.
  
  all u: User | u.suggested = u.follows.follows - u
} }

pred S22 { {
	// Suggested are other users followed by followed users, but not yet followed.
	all u : User, u2 : u.follows, u3 : u2.follows | u3 in u.follows implies not (u3 in u.suggested)
} }

pred S23 { {
	// Suggested are other users followed by followed users, but not yet followed.
  
  all disj x,y: User | x!=y and  y in x.suggested implies y in x.^follows
	
} }

pred S24 { {
	// Suggested are other users followed by followed users, but not yet followed.
  all u:User | no(u.suggested & (u.follows+u)) 
	
} }

pred S25 { {
	// Suggested are other users followed by followed users, but not yet followed.
  all x,y,z : User | y in x.suggested iff y in z.follows and z in x.follows and y not in x.follows
	
} }

pred S26 { {
	// Suggested are other users followed by followed users, but not yet followed.
  	all u1, u2, u3 : User | (u1 != u2 and u2 != u3 and u1 != u3 and u2 in u1.follows and u3 in u2.follows and u3 not in u1.follows) iff u3 in u1.suggested
	
} }

pred S27 { {
	// Suggested are other users followed by followed users, but not yet followed.
  	all u: User | u.suggested in ( (u.^follows) - u.follows )
	
} }
