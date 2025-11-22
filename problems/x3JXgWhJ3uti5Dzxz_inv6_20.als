sig User { follows : set User, sees : set Photo, posts : set Photo, suggested : set User } sig Influencer extends User {} sig Photo { date : one Day } sig Ad extends Photo {} sig Day {}
pred S0 { {
	// Influencers post every day.
	all d : Day, i : Influencer | d in i.posts.date
} }

pred S1 { {
	// Influencers post every day.
  

} }

pred S2 { {
	// Influencers post every day.
  all d: Day, i: Influencer | i.posts.date in d

} }

pred S3 { {
	// Influencers post every day.
  all d:Day, i:Influencer | d in i.posts

} }

pred S4 { {
	// Influencers post every day.
    Influencer.posts.date = Day

} }

pred S5 { {
	// Influencers post every day.
	all d: Day | all i: Influencer | i.posts in d
} }

pred S6 { {
	// Influencers post every day.
    all i: Influencer | all d: Day|  i.posts.date = d

} }

pred S7 { {
	// Influencers post every day.
  


  


 
    
 
     Influencer in posts.date.Day
} }

pred S8 { {
	// Influencers post every day.
  all u: Influencer, d: Day, p: Photo | p in u.posts and d in p.date 

} }

pred S9 { {
	// Influencers post every day.
  	all u : User | all p : Photo.date | u in Influencer implies p in u.posts
  

} }

pred S10 { {
	// Influencers post every day.
	all i : Influencer | all d : Day | one p : i.posts | p.date = d
} }

pred S11 { {
	// Influencers post every day.
  all x : Influencer | some y: Photo | all z: Day | y in date.z and y in posts.x
} }

pred S12 { {
	// Influencers post every day.
	all d: Day | some i: Influencer | i.posts.date in d
} }

pred S13 { {
	// Influencers post every day.
	all x : User | x in Influencer implies (all d : Day | some p : Photo | x->p in posts implies p->d in date)

} }

pred S14 { {
	// Influencers post every day.
  all i: Influencer, d: Day | some i.posts.date
} }

pred S15 { {
	// Influencers post every day.
	all i:Influencer, d: Day | some p:Photo, a:Ad | (p in i.posts and p.date = d) or 
  													(a in i.posts and a.date = d)
} }

pred S16 { {
	// Influencers post every day.
  	all i: Influencer | some p : Photo | all a : Day | p in i.posts and a in p.date

} }

pred S17 { {
    // Influencers post every day.
  	all i: Influencer | all d: Day | some p: Photo | p.date = d

} }

pred S18 { {
	// Influencers post every day.
  all i : Influencer | all d : Day | lone p : Photo | d in p.date and p in i.posts
} }

pred S19 { {
	// Influencers post every day.
  all i:Influencer, d:Day, z:Photo | z in i.posts implies not some dx:Day | dx not in i.posts.date

} }
