sig User { follows : set User, sees : set Photo, posts : set Photo, suggested : set User } sig Influencer extends User {} sig Photo { date : one Day } sig Ad extends Photo {} sig Day {}
pred S0 { {
	// Users can see ads posted by everyone, 
	// but only see non ads posted by followed users.
  all u: User | u.sees in (u.follows.posts + Ad)
} }

pred S1 { {
	// Users can see ads posted by everyone, 
	// but only see non ads posted by followed users.
  	all u: User | u.sees = {Ad + u.follows.posts} 

} }

pred S2 { {
	// Users can see ads posted by everyone, 
	// but only see non ads posted by followed users.

} }

pred S3 { { 
	// Users can see ads posted by everyone, 
	// but only see non ads posted by followed users.
	
  	
  	all u: User | (u.follows.posts + Ad) in u.sees 
  	
} }

pred S4 { {
	// Users can see ads posted by everyone, 
	// but only see non ads posted by followed users.
  	

  	
  
  	
    
    
      
       
    
  	
  	all u: User + Influencer, a: Ad | a in u.sees
} }

pred S5 { {
	// Users can see ads posted by everyone, 
  	all u : User, add : Ad | add in u.sees 
	// but only see non ads posted by followed users.
  	all u : User, p : Photo |
  		
  		(p in u.sees and not p in Ad) implies
  		
  		some user : User | p in user.posts and user in u.follows
  

} }

pred S6 { {
    // Users can see ads posted by everyone,
    
    all u: User |
        u.sees in Ad and
        (all p: u.sees - Ad | some f: u.follows | p in f.posts - Ad)
} }

pred S7 { {
	// Users can see ads posted by everyone, 
	// but only see non ads posted by followed users.
   all u: User, p: Photo |
        (p in Ad) or (some f: u.follows | p in f.posts) implies p in u.sees
	
} }
