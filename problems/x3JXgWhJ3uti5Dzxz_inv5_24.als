sig User { follows : set User, sees : set Photo, posts : set Photo, suggested : set User } sig Influencer extends User {} sig Photo { date : one Day } sig Ad extends Photo {} sig Day {}
pred S0 { {
	// Influencers are followed by everyone else.
    all u : User | all i : Influencer | u != i implies i in u.follows
} }

pred S1 { {
	// Influencers are followed by everyone else.
    all u : User, i: Influencer | i in u.follows
} }

pred S2 { {
	// Influencers are followed by everyone else.
  	all i: Influencer | all u: (User + Influencer) | i != u && i in u.follows

} }

pred S3 { {
	// Influencers are followed by everyone else.
	all i : Influencer, u : User - Influencer | i in u.follows
} }

pred S4 { {
	// Influencers are followed by everyone else.

} }

pred S5 { {
	// Influencers are followed by everyone else.
  
  
  all u: User| all i: Influencer | u in i.follows

} }

pred S6 { {
	// Influencers are followed by everyone else.
	all i: Influencer | i in User.follows
} }

pred S7 { {
	// Influencers are followed by everyone else.
	all inf: Influencer, user: User | user != inf => user in inf.follows
} }

pred S8 { {
	// Influencers are followed by everyone else.

      all x : Influencer | follows.x  in User-x         

} }

pred S9 { {
	// Influencers are followed by everyone else.

  follows.Influencer = User
} }

pred S10 { {
	// Influencers are followed by everyone else.
  all i : Influencer | i in (User-Influencer).follows 

} }

pred S11 { {
	// Influencers are followed by everyone else.
	all i : Influencer | i in (User-i).follows
} }

pred S12 { {
	// Influencers are followed by everyone else.
  all u: User - Influencer | some i: Influencer | i in u.follows

} }

pred S13 { {
	// Influencers are followed by everyone else.
  
  all i: Influencer | all user: User - Influencer | user in i.follows

} }

pred S14 { {
	// Influencers are followed by everyone else.
	all u : User | u in Influencer => u in u.follows 
} }

pred S15 { {
	// Influencers are followed by everyone else.
	all u : User | u.follows in Influencer
} }

pred S16 { {
	// Influencers are followed by everyone else.
  all u: User | u in Influencer.follows 

} }

pred S17 { {
	// Influencers are followed by everyone else.
  all u: User | Influencer in u.follows and u not in u.follows
  
  
} }

pred S18 { {
	// Influencers are followed by everyone else.
  
  
  all u: User-Influencer| u in Influencer.follows

} }

pred S19 { {
	// Influencers are followed by everyone else.
	all x : User | all z : Influencer | x.follows in z
} }

pred S20 { {
	// Influencers are followed by everyone else.
  	all u : User-Influencer | follows.u in Influencer

} }

pred S21 { {
	// Influencers are followed by everyone else.
	all i : Influencer | no i.follows
} }

pred S22 { {
	// Influencers are followed by everyone else.
	all i: Influencer | i in follows.User
} }

pred S23 { {
	// Influencers are followed by everyone else.
  all u: User, i: Influencer | some Influencer & u.follows implies i in u.follows 

} }
