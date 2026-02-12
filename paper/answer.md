Here are several *different* Alloy specifications you could use for the requirement **“A professor cannot teach colleagues”**, without introducing new signatures. Each one encodes a slightly different interpretation of *colleagues* and/or *cannot teach*.

---

## 1) “No professor may teach a course that any other professor is enrolled in”
Interpretation: professors are colleagues if they are professors; teaching colleagues means “teaching a course taken by another professor”.

```alloy name=spec1_no_prof_teaches_course_with_prof_enrolled.als
fact NoProfessorTeachesColleagues_v1 {
  all prof : Professor |
    no (prof.teaches & (Professor - prof).enrolled)
}
```

Equivalent phrasing:

```alloy name=spec1b_equivalent.als
fact NoProfessorTeachesColleagues_v1b {
  all prof : Professor, other : Professor |
    other != prof implies no (prof.teaches & other.enrolled)
}
```

---

## 2) “No professor may be enrolled in any course taught by another professor”
Interpretation: forbid the *situation* of one professor teaching another (direction doesn’t matter; it prevents colleagues-from-being-students-of-each-other).

```alloy name=spec2_no_prof_enrolled_in_any_course_taught_by_prof.als
fact NoProfessorTeachesColleagues_v2 {
  no (Professor.enrolled & Professor.teaches)
}
```

This is symmetric in effect: if there exists `p1, p2` professors and `c` with `c in p1.teaches` and `c in p2.enrolled`, it’s disallowed.

---

## 3) “If two professors are both enrolled in the same course, neither may teach the other’s courses”
Interpretation: “colleagues” means “co-students” (they share at least one enrolled course). Then a professor cannot teach a course that a colleague is enrolled in.

```alloy name=spec3_colleagues_as_coenrolled_professors.als
fact NoProfessorTeachesColleagues_v3 {
  all p, q : Professor |
    (some (p.enrolled & q.enrolled) and p != q) implies
      no (p.teaches & q.enrolled)
}
```

This is weaker than (1)/(2) because it only applies when they already share an enrolled course.

---

## 4) “Professors who teach the same course are colleagues; they can’t teach each other”
Interpretation: colleagues are *co-instructors* (teach at least one common course). Then disallow teaching a course the colleague is enrolled in.

```alloy name=spec4_colleagues_as_coteachers.als
fact NoProfessorTeachesColleagues_v4 {
  all p, q : Professor |
    (some (p.teaches & q.teaches) and p != q) implies
      no (p.teaches & q.enrolled)
}
```

Again: only constrains pairs that co-teach something.

---

## 5) “No professor can teach any course where a different professor is enrolled (global form)”
Interpretation: *any* course taught by *any* professor must have **no professors enrolled** (except possibly the teacher, but that’s already prevented by your `no p.teaches & p.enrolled`).

```alloy name=spec5_courses_taught_by_profs_have_no_prof_enrolled.als
fact NoProfessorTeachesColleagues_v5 {
  all c : Course |
    (some (Professor & teaches.c)) implies
      no (Professor.enrolled & c)
}
```

This is a different “shape” than (2): it’s stated per-course rather than via relation intersection.

---

## 6) “A professor cannot teach any course that is enrolled by *any* professor (including themselves)”
Interpretation: even stronger blanket rule; but since self-teach is already ruled out, the practical added constraint is “no professor teaches a course with any professors enrolled”.

```alloy name=spec6_no_prof_teaches_any_course_with_prof_enrolled.als
fact NoProfessorTeachesColleagues_v6 {
  all p : Professor |
    no (p.teaches & Professor.enrolled)
}
```

This is close to (1) but doesn’t subtract `p` from `Professor` (redundant given your existing “No one teaches itself” fact).

---

## 7) “Colleagues are people working on at least one common project; professors can’t teach a colleague”
Interpretation: colleagues are defined by collaboration (shared projects). Then: if a professor teaches a course, nobody who is a “project-colleague” of that professor may be enrolled in that course.

```alloy name=spec7_colleagues_as_shared_project_collaborators.als
fact NoProfessorTeachesColleagues_v7 {
  all p : Professor |
    let colleagues = { q : Person | q != p and some (p.workson & q.workson) } |
      no (p.teaches & colleagues.enrolled)
}
```

If you want “colleagues” to mean “shared project with another **professor**”:

```alloy name=spec7b_colleagues_as_shared_project_with_professors.als
fact NoProfessorTeachesColleagues_v7b {
  all p : Professor |
    let colleagues = { q : Professor | q != p and some (p.workson & q.workson) } |
      no (p.teaches & colleagues.enrolled)
}
```

---

## 8) “Colleagues are people who teach in the same department-like bundle: share at least one student”
Interpretation: no departments exist, so approximate “colleagues” as professors who share at least one enrolled student (teach courses that have at least one common student). Then they can’t teach each other (i.e., can’t teach a course the other is enrolled in).

```alloy name=spec8_colleagues_as_sharing_students.als
fact NoProfessorTeachesColleagues_v8 {
  all p, q : Professor |
    (p != q and some ((p.teaches.~enrolled) & (q.teaches.~enrolled))) implies
      no (p.teaches & q.enrolled)
}
```

(`p.teaches.~enrolled` = the set of persons enrolled in any course taught by `p`.)

---

### If you tell me which meaning you intend for “colleagues” (co-instructors, fellow professors, collaborators on projects, etc.), I can recommend the cleanest of the above and/or simplify it to a minimal idiomatic Alloy constraint.