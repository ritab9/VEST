from statistics import mean

def average(grades):
    summative = grades.filter(type="S")
    a1=[]
    for s in summative:
        a1.append(s.percent())
    if a1:
        s1=mean(a1)
    else:
        s1=None

    formative=grades.filter(type="F")
    a2 = []
    for f in formative:
        a2.append(f.percent())
    if a2:
        s2=mean(a2)
    else:
        s2=None

    #todo Have school preferences here.
    # For now we will do 80% Summative and 20% Formative

    if s1 and s2:
        a=round(s1*0.8+s2*0.2,2)
    elif s1: a=round(s1,2)
    elif s2: a=round(s2,2)
    else:
        a=None

    return a