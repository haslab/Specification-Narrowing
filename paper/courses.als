sig Person {
	teaches : set Course,
	enrolled : set Course,
	workson : set Project
}

sig Professor, Student in Person {}

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
