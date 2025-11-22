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
