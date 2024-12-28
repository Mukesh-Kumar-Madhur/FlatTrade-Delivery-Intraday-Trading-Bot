import pandas as pd
from datetime import datetime
import os
import mail

# Define the initial structure of the DataFrame
columns = ['Stock', 'entry_date', 'entry_price', 'target', 'exit_price', 'status', 'exit_date', 'Quantity', 'Profit', 'Charges', 'Net_Profit/Loss', 'day_count', 'Session']

def ensure_database_exists():
    # Check if the database file exists, if not create it
    if not os.path.exists('Database_equity.csv'):
        df = pd.DataFrame(columns=columns)
        df.to_csv('Database_equity.csv', index=False)


def get_qty(stock, ltp):
        
    # Load the database
    df = pd.read_csv('Database_equity.csv')
    
    # Filter rows based on the given conditions
    mask = (df['Stock'] == stock) & (df['status'] == 'Open') & (df['target'] <= ltp)
    
    # Calculate the sum of quantities for matching rows
    total_quantity = df.loc[mask, 'Quantity'].sum()
    
    return total_quantity



def stock_li_to_monitor():
    df = pd.read_csv('Database_equity.csv')
    
    # Create a mask to filter rows where the status is 'Open'
    mask = (df['status'] == 'Open')
    
    # Extract unique symbols with 'Open' status and add them to the list
    li_stocks = df.loc[mask, 'Stock'].unique().tolist()
    
    return li_stocks



def db_entry(stock, entry_price, quantity):
    ensure_database_exists()
    
    df = pd.read_csv('Database_equity.csv')
    
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Format datetime to seconds
    
    # Determine session and calculate target based on time of entry
    if datetime.strptime(current_datetime, '%Y-%m-%d %H:%M:%S').time() >= datetime.strptime("09:15:00", "%H:%M:%S").time() and \
        datetime.strptime(current_datetime, '%Y-%m-%d %H:%M:%S').time() <= datetime.strptime("09:20:00", "%H:%M:%S").time():
        target = entry_price * 1.0025
        session = 'Morning'
    elif datetime.strptime(current_datetime, '%Y-%m-%d %H:%M:%S').time() >= datetime.strptime("14:59:00", "%H:%M:%S").time() and \
        datetime.strptime(current_datetime, '%Y-%m-%d %H:%M:%S').time() <= datetime.strptime("16:31:00", "%H:%M:%S").time():
        target = entry_price * 1.004
        session = 'Evening'
    else:
        target = entry_price * 1.0025  # Default target calculation
        session = 'Other'
    
    # Create new entry
    new_entry = pd.DataFrame({
        'Stock': [stock],
        'entry_date': [current_datetime],
        'entry_price': [entry_price],
        'target': [target],
        'exit_price': [None],
        'status': ['Open'],
        'exit_date': [None],
        'Quantity': [quantity],
        'Profit': [None],
        'Charges': [None],
        'Net_Profit/Loss': [None],
        'day_count': [None],
        'Session': [session]
    })
    
    # Append to the DataFrame
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv('Database_equity.csv', index=False)

def db_exit(stock, exit_price):
    ensure_database_exists()
    
    df = pd.read_csv('Database_equity.csv')
    
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Format datetime to seconds
    
    # Find the row to update
    mask = (df['Stock'] == stock) & (df['status'] == 'Open') & (df['target'].astype(float) <= exit_price)
    
    # Update exit details for matching rows
    df.loc[mask, 'exit_price'] = exit_price
    df.loc[mask, 'status'] = 'Exit'
    df.loc[mask, 'exit_date'] = current_datetime
    
    # Ensure correct datetime parsing
    df['entry_date'] = pd.to_datetime(df['entry_date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    df['exit_date'] = pd.to_datetime(df['exit_date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    
    # Calculate Profit, Charges, Net Profit/Loss, and day count
    df.loc[mask, 'Profit'] = df['exit_price'].astype(float) - df['entry_price'].astype(float)
    df.loc[mask, 'day_count'] = (df['exit_date'] - df['entry_date']).dt.days
    
    # Update charges calculation based on session
    is_same_day_exit = df.loc[mask, 'day_count'] == 0

    morning_charge = 0.0001 * df['entry_price'] + 0.0004 * df['exit_price'].astype(float)
    evening_charge = 23 + 0.00104 * df['entry_price'] + 0.00104 * df['exit_price'].astype(float)

    df.loc[mask & (df['Session'] == 'Morning') & is_same_day_exit, 'Charges'] = morning_charge
    df.loc[mask & (df['Session'] == 'Morning') & ~is_same_day_exit, 'Charges'] = evening_charge
    df.loc[mask & (df['Session'] == 'Evening') & is_same_day_exit, 'Charges'] = morning_charge
    df.loc[mask & (df['Session'] == 'Evening') & ~is_same_day_exit, 'Charges'] = evening_charge
    df.loc[mask & (df['Session'] == 'Other') & is_same_day_exit, 'Charges'] = morning_charge
    df.loc[mask & (df['Session'] == 'Other') & ~is_same_day_exit, 'Charges'] = evening_charge
    
    df.loc[mask, 'Net_Profit/Loss'] = df['Profit'] - df['Charges']
    
    df.to_csv('Database_equity.csv', index=False)

# # Example Usage
# db_entry('Tata', 100, 10)
# db_entry('Reliance', 200, 5)
# db_entry("Ingerrand-EQ", 4555, 4)

# db_exit('Tata', 102)
# db_exit('Reliance', 250)
# df = pd.read_csv('Database_equity.csv')
# print(df)




def increase_target():
    ensure_database_exists()
    
    # Load the database
    df = pd.read_csv('Database_equity.csv')
    
    # Apply the increase for rows with status "Open"
    mask = df['status'] == 'Open'
    df.loc[mask, 'target'] = df.loc[mask, 'target'] * 1.001  # Increase by 0.1%
    
    # Extract rows that were updated
    df_updated_rows = df[mask].copy()
    
    # Save the updated DataFrame back to the CSV file
    df.to_csv('Database_equity.csv', index=False)
    
    # Format updated rows for email
    if not df_updated_rows.empty:
        # Convert updated rows to an HTML table
        updated_rows_html = df_updated_rows.to_html(index=False, border=1, justify='center', classes='table table-striped')
        
        # HTML email body
        email_body = f"""
        <html>
        <head>
        <style>
        table {{
            width: 100%;
            border-collapse: collapse;
            font-family: Arial, sans-serif;
            font-size: 14px;
        }}
        th, td {{
            text-align: center;
            border: 1px solid #dddddd;
            padding: 8px;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        </style>
        </head>
        <body>
        <p>Hi,</p>
        <p>All stocks with 'Open' status have had their target increased by 0.1%.</p>
        <p><strong>Details:</strong></p>
        {updated_rows_html}
        <p>Best regards,</p>
        <p>Your Stock Management System</p>
        </body>
        </html>
        """
        
        # Send the email with the formatted table
        mail.mail_with_text(
            "Target Update Successful",
            email_body,
            is_html=True  # Indicates that the email body contains HTML content
        )
    else:
        # If no rows were updated, send a plain-text notification
        mail.mail_with_text(
            "Target Update Notification",
            "Hi,\n\nNo stocks with 'Open' status were found, so no targets were updated.\n\nBest regards,\nYour Stock Management System"
        )
    
    print("Targets for open stocks have been increased by 0.1% successfully.")


