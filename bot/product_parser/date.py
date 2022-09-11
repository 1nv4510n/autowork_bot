from datetime import date

def get_quarter() -> str:
    quarter = (date.today().month - 1) // 3 + 1
    
    match quarter:
        case 1:
            return 'I'
        case 2:
            return 'II'
        case 3:
            return 'III'
        case 4:
            return 'IV'
        
def get_year() -> str:
    return str(date.today().year)