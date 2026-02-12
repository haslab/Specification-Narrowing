sig Person {
	teaches : set Course,
	enrolled : set Course,
	workson : set Project
}

sig Professor in Person {}
sig Student in Person {}

sig Course {
	projects : set Project
}

sig Project {}

fact Assumptions {
	// All courses have professors
	all c : Course | some teaches.c
	// Only professors teach
	teaches.Course in Professor
	// Only stuents can be enrolled
	enrolled.Course in Student
	// Projects are not shared between courses
	all p : Project | lone projects.p
	// No one teaches itself
	all p : Person | no p.teaches & p.enrolled
	// Can only work on projects of enrolled courses
	all p : Person | p.workson in p.enrolled.projects
}

assert OnlyStudentsWorkOnProjects {
	workson.Project in Student
} 
check OnlyStudentsWorkOnProjects for 4 expect 0

pred Spec1 {
  all p : Professor |
    no (p.teaches & (Professor - p).enrolled)
}

pred Spec2 {
  all p, q : Professor |
    (some (p.enrolled & q.enrolled) and p != q) implies
      no (p.teaches & q.enrolled)
}

pred Spec3 {
  all p, q : Professor |
    (some (p.teaches & q.teaches) and p != q) implies
      no (p.teaches & q.enrolled)
}

pred Spec4 {
  all p : Professor |
    let colleagues = { q : Person | q != p and some (p.workson & q.workson) } |
      no (p.teaches & colleagues.enrolled)
}

pred Spec5 {
  all p : Professor |
    let colleagues = { q : Professor | q != p and some (p.workson & q.workson) } |
      no (p.teaches & colleagues.enrolled)
}

pred Spec6 {
  all p, q : Professor |
    (p != q and some ((p.teaches.~enrolled) & (q.teaches.~enrolled))) implies
      no (p.teaches & q.enrolled)
}

run Test1 {
	some disj a,b,c,d,e,f,g,h : univ {
		Course = g + h
		Person = b + c + f
		Professor = c + f
		Project = a + d + e
		Student = b + c + f
		enrolled = b->g + b->h + f->h
		projects = g->a + g->e + h->d
		teaches = c->h + f->g
		workson = b->a + b->d + b->e + f->d
	}
} for 3 expect 1

run Test2 {
	some disj a,b,c,d,e,f,g : univ {
		Course = d + e
		Person = a + b + c
		Professor = a + b + c
		Project = f + g
		Student = a + b + c
		enrolled = b->e
		projects = e->f
		teaches = a->e + b->d + c->d + c->e
		no workson
	}
} for 3 expect 0

run Test3 {
	some disj a,b,c,d,e,f : univ {
		Course = b + c + f
		Person = a + d + e
		Professor = a + d + e
		no Project
		Student = a + e
		enrolled = a->b + a->c + e->b
		no projects
		teaches = d->b + e->c + e->f
		no workson
	}
} for 3 expect 1
