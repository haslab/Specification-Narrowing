sig User {
	follows : set User,
	sees : set Photo, 
	posts : set Photo, 
	suggested : set User 
}
sig Influencer extends User {}
sig Photo { 
	date : one Day 
} 
sig Ad extends Photo {} 
sig Day {}

pred S1 {all p: Photo | one (posts.p)}
pred S2 {}
pred S3 {all p : Photo | some u : User | p in u.posts}
pred S4 {all x : Photo | lone posts.x}
pred S5 {all p: Photo, u: User | p in u.posts}
pred S6 {all x: Photo | one x.posts}
pred S7 {all p: Photo | one u: User | u.posts = p}
pred S8 {one u : User | all p : Photo | p in u.posts}
pred S9 {all disj u1 : User, u2 : User | no (u1.posts & u2.posts)}
pred S10 {all u : User | lone u.posts}
