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

pred S1 {all u: User | some u.posts & Ad implies u.posts in Ad}
pred S2 {}
pred S3 {all u : User | some ad : Ad | ad in u.posts implies u.posts in Ad}
pred S4 {all u:User | some p:Photo | p in Ad and p in u.posts implies u.posts in Ad}
pred S5 {all u : User | u.posts in Ad}
pred S6 {all u:User | Ad in u.posts implies u.posts in Ad}
pred S7 {all u : User | some a : u.posts | a in Ad implies u.posts in Ad}
pred S8 {all u: User | not u in (posts.Photo & posts.Ad)}
pred S9 {all u: User | some(u.posts & Ad) implies (u.posts = Ad)}
pred S10 {all u : User | (one u.posts & Ad) implies u.posts in Ad}
pred S11 {all u:User | one up: u.posts | up in Ad implies u.posts in Ad}
pred S12 {all x: User | (some y: Photo | x->y in posts and y in Ad) implies all z: Photo | x->z in posts and z in Ad }
pred S13 {all x: User | some y: Ad | y in x.posts implies (all z: Photo | z in x.posts and z in Ad)}
pred S14 {all u : User, p : u.posts | Ad in p implies p = Ad}
pred S15 {all u : User, p : Photo | p in Ad implies u.posts in Ad}
pred S16 {all u : User | some pa : u.posts & Ad | #pa > 0 implies (all p : u.posts | p in Ad)}
