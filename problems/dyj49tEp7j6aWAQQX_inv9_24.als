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

pred S12 { {
	// The workstations form a single line between begin and end
  all w: Workstation | one w.succ
} }

pred S13 { {
	// The workstations form a single line between begin and end
	end in begin.^succ

} }

pred S14 { {
	// The workstations form a single line between begin and end
  	begin not in Workstation.^succ
  	begin.^succ = Workstation - begin
  	all w : Workstation | w not in w.succ
  	end in Workstation.^succ or lone Workstation
  	no end.succ
} }

pred S15 { {
	// The workstations form a single line between begin and end
  	all ws: Workstation | ws in begin.*succ and end in ws.*succ
} }

pred S16 { {
	// The workstations form a single line between begin and end
	no succ.begin
    no end.succ
    Workstation = begin.*succ
} }

pred S17 { {
	// The workstations form a single line between begin and end
	all w: Workstation | w not in w.^succ
  	
  	all w: Workstation - end | one s: Workstation | s in w.succ
  	
  	all e: end | all w: Workstation | w not in e.succ
  	
  	all b: begin | all w: Workstation | b not in w.succ
} }

pred S18 { {
	// The workstations form a single line between begin and end
  all w: Workstation | (w not in end) implies one w.succ
} }

pred S19 { {
	// The workstations form a single line between begin and end
  no end.succ
  Workstation in begin.^succ
} }

pred S20 { {
	// The workstations form a single line between begin and end
  all w : Workstation | one begin.succ & w and one w.^succ & end and (w not in w.^succ or w in end)
	
} }

pred S21 { {
	// The workstations form a single line between begin and end
	Workstation = begin.*succ
  	Workstation = end.*(~succ)
  	
  	all ws:Workstation - end - begin | one ws.succ and one ws.~succ
  
  	all ws:Workstation | ws not in ws.^succ
  
  	one end.~succ
  	no end.succ
  
  	one begin.succ
  	no begin.~succ
  
} }

pred S22 { {
	// The workstations form a single line between begin and end
	all w : Workstation | (w = end or some w.succ) and (w != end implies one w.succ) and (w != begin implies one w.~succ)
} }

pred S23 { {
	// The workstations form a single line between begin and end
	all ws : Workstation | ws not in ws.^succ
  	all ws1, ws2 : Workstation | ws1 != ws2 implies ws1 in ws2.^succ or ws2 in ws1.^succ
} }
