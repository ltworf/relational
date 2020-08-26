from relational.optimizer import optimize_program

a = optimize_program('''ppl_skills = people ⧓skills
ppl_skills1 = ppl_skills ∪ (people ⧓skills)
ppl_skills ∩ ppl_skills1 ⧓ dates''', {})

assert a == '''optm_a = people⧓skills
optm_b = optm_a⧓dates'''
