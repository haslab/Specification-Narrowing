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
