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
