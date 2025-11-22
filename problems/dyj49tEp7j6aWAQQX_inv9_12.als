sig Workstation { workers : set Worker, succ : set Workstation } one sig begin, end in Workstation {} sig Worker {} sig Human, Robot extends Worker {} abstract sig Product { parts : set Product } sig Material extends Product {} sig Component extends Product { workstation : set Workstation } sig Dangerous in Product {}
pred S0 { {
	// The workstations form a single line between begin and end
  
  	all w : Workstation | w in begin.*succ
  
  	all w : Workstation - end | one w.succ
  
  	no end.succ
	
} }

pred S1 { {
	// The workstations form a single line between begin and end
  	begin not in Workstation.^succ
  	(Workstation-begin) in begin.*succ
  	all w:Workstation | w not in w.*succ
  	no end.succ
} }

pred S2 { {
	// The workstations form a single line between begin and end
  	all w: Workstation | all wStart: (Workstation & begin) | 
 		wStart not in w.^succ
  	all wStart: (Workstation & begin) - end | one wEnd: (Workstation & end) |
  		wEnd in wStart.^succ
  	all w: Workstation | no w.succ implies w in begin
  	all w: Workstation | w not in w.^succ
} }

pred S3 { {
	// The workstations form a single line between begin and end
	
} }

pred S4 { {
	// The workstations form a single line between begin and end
    all ws : Workstation | ws in begin.*succ
} }

pred S5 { {
	// The workstations form a single line between begin and end
	all w: Workstation | w not in w.^succ
} }

pred S6 { {
	// The workstations form a single line between begin and end
  	all ws: Workstation | (ws in begin.^succ or ws = begin) and (end in ws.^succ or ws = end) and ws not in ws.^succ
} }

pred S7 { {
	// The workstations form a single line between begin and end
  	all w: (Workstation+begin+end) | w in begin.*succ and w not in end.^succ
} }

pred S8 { {
	// The workstations form a single line between begin and end
	one w1 : Workstation, w3 : Workstation | all w2 :  Workstation - w1 - w3 |  w2 & w3 in w1.^succ && w2 & w1 in w3.^succ && #(w2.succ) = 1
  	 
} }

pred S9 { {
	// The workstations form a single line between begin and end
	all wstation: Workstation | wstation in end implies no wstation.succ
  	all wstation: Workstation | wstation in begin or wstation in end
  	all wstation: Workstation | wstation in begin and wstation not in end 
  		implies end in wstation.^succ
  	all wstation: Workstation | no (wstation.succ & wstation)
} }

pred S10 { {
	// The workstations form a single line between begin and end
	all w: Workstation | one begin.^succ & w
} }

pred S11 { {
	// The workstations form a single line between begin and end
	end in begin.*succ

} }
