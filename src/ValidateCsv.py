from petl import fromcsv, validate, values

def validate_csv(path):
    table = fromcsv("csv\\" + path)
    header = ("Address", " City", " State", " ZIP", " Backroom Stock", " Floor Stock", " In Transit Stock", " Price", " Aisles")
    problems = validate(table, header=header)
    # print(problems.lookall())
    
    problems = list(values(problems, "name", "row", "field", "value", "error"))
    
    if len(problems) == 0:
        return False
    
    if "__header__" in problems[0]:
        return True
    
    return False