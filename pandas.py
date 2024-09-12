import pandas as pd
import requests
from decimal import Decimal

pd.options.mode.chained_assignment = None

items_to_order_report = 'https://your/list/of/items/to/order/odata/?$format=json'

report_response = requests.get(url=items_to_order_report)


whses_code = {

        "WA":1,"OR":2,'CA':3

        }


def items_report():
    if report_response.status_code == 200:
        so_dic = report_response.json()

        so_df = pd.DataFrame(so_dic['value'])
        
        so_df_sanmar = so_df[so_df['AccountName'] == 'S&S Activewear']
        
        required_columns = ['AlternateID', 'SOColor', 'SOSize', 'InventoryID', 'Qty', 'OrderNbr']
        if not all(col in so_df_sanmar.columns for col in required_columns):
            return "Missing one or more required columns in the data"

        so_df_sanmar['Info'] = so_df_sanmar.apply(
            lambda row: '--'.join([
                str(row['AlternateID']),
                str(row['SOColor']),
                str(row['SOSize']),
                str(row['InventoryID']),
                str(row["Qty"])
            ]), axis=1
        )
        
        grpby_po = so_df_sanmar.groupby('OrderNbr').agg(
            Info=('Info', lambda x: '|'.join(x)),
            TotalQty=('Qty', 'sum')
        ).reset_index()
        
        grpby_po.columns = ["OrderNbr", "Info", "TotalQty"]
        print(grpby_po['TotalQty'])

        group1 = grpby_po[grpby_po['TotalQty'] <= 2]
        group2 = grpby_po[(grpby_po['TotalQty'] >= 3) & (grpby_po['TotalQty'] <= 6)]
        group3 = grpby_po[(grpby_po['TotalQty'] >= 7) & (grpby_po['TotalQty'] <= 10)]
        group4 = grpby_po[(grpby_po['TotalQty'] > 10)]

        grouped_data = {
            'Group1_<=2': group1.to_dict(orient='records'),
            'Group2_3to6': group2.to_dict(orient='records'),
            'Group3_7to10': group3.to_dict(orient='records'),
            'Group4': group4.to_dict(orient='records')

        }

        return grouped_data

    else:
        return f"Error code: {report_response.status_code}"


def get_unique_order_numbers():
    return list(set(items_report()['OrderNbr']))    
    