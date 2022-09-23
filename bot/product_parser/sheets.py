
import gspread
from . import date

gc = gspread.service_account(filename='bot/product_parser/auth.json')



class GoogleSheets:
    def __init__(self, spreadsheet_url: str, worksheet_name: str) -> None:
        self.spreadsheet = gc.open_by_url(url=spreadsheet_url)
        self.worksheet = self.spreadsheet.worksheet(title=worksheet_name)
        
    def fill_line(self, data: dict) -> None:
        values = [
            data['product_name'],
            'шт',
            'шт',
            str(data['product_price']).replace('.', ','),
            str(round(float(data['product_price']) * 0.8, 2)).replace('.', ','),
            '',
            str(round(float(data['product_price']) * 0.8, 2)).replace('.', ','),
            date.get_year(),
            date.get_quarter(),
            data['company_info']['company_name'],
            data['company_info']['company_kpp'] if data['company_info']['company_kpp'] is not None else '-',
            data['company_info']['company_inn'],
            data['product_url'],
            data['product_city'],
            data['company_info']['table_status'],
            'Том прайс листов Книга 3'
        ]

        
        # self.worksheet.append_row(values=values, value_input_option='USER_ENTERED', table_range='A18')
        response = self.worksheet.update(f'D{len(self.worksheet.col_values(4)) + 1}', [values])
        print(response)