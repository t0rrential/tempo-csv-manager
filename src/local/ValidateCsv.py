from petl import fromcolumns, validate, values
from csv import reader as r
from io import StringIO

def csvConverter(path):
    with open("csv\\" + path, 'r') as file:
        reader = r(file)
        data = list(reader)

    csvString = "\n".join([",".join(row) for row in data[:len(data)-1]])
    return StringIO(csvString)

def validate_csv(path):
    with open("csv\\" + path, 'r') as file:
        reader = r(file)
        data = list(reader)
        
    header = data[0]  # First row is the header
    rows = data[1:len(data)-1]   # Remaining rows are the content

    # Step 3: Convert to a PETL table
    table = fromcolumns(zip(*rows), header=header)
    problems = validate(table, header=header)
    # print(problems.lookall())
    
    problems = list(values(problems, "name", "row", "field", "value", "error"))
    # print(f"{path} {problems}")
    
    if len(problems) == 0:
        return False
    
    if "__header__" in problems[0]:
        return True
    
    return False