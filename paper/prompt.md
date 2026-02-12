Consider the following Alloy model:
```
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
}```

Give me possible different specifications for the requirement "A professor cannot teach colleagues". Do not add sigs to the model.