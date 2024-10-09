# eliminar columnas

import pandas as pd
import re
import datetime

def read_data(url): 
    df = pd.read_excel(url)
    return df

def drop_columns(df): 
    '''
    Drop useless columns
    '''
    
    df.drop(columns=["Case Number.1"], inplace=True)
    df.drop(columns=["Unnamed: 21"], inplace=True)
    df.drop(columns=["Unnamed: 22"], inplace=True)
    df.drop(columns=["Case Number"], inplace=True)
    df.drop(columns=["href formula"], inplace=True)
    df.drop(columns=["href"], inplace=True)
    df.drop(columns=["pdf"], inplace=True)
    
    return df
    

# Clean and Standarize Date Formats

def clean_date(date_str):
    # Check if the input is NaT (Not a Time)
    if pd.isna(date_str):
        return pd.NaT
    
    # Convert datetime objects to string
    if isinstance(date_str, (pd.Timestamp, datetime.datetime)):
        date_str = date_str.strftime('%d %b %Y')
    
    # Ensure the input is a string
    if not isinstance(date_str, str):
        return date_str
    
    # Remove words like 'Reported', 'Ca.', 'Early', 'Late', 'Between', 'Before', 'After', 'Anniversary Day', 'No date', and extra spaces
    date_str = re.sub(r'Reported|Ca\.|Ca|Early|Late|Between|Before|After|Anniversary Day|No date|During the war|Before the war|Said to be|World War II|a few years before|early|late|between|before|after|anniversary day|no date|during the war|before the war|said to be|world war ii', '', date_str, flags=re.IGNORECASE).strip()
    
    # Remove suffixes like '.a' and '.b'
    date_str = re.sub(r'\.\w$', '', date_str).strip()
    
    # Replace inconsistent formats
    date_str = re.sub(r'(\d{2})-(\w+)-(\d{4})', r'\1 \2 \3', date_str)  # 09-Sep-2023 -> 09 Sep 2023
    date_str = re.sub(r'(\d{2}) (\w+)-(\d{4})', r'\1 \2 \3', date_str)  # 09 Sep-2023 -> 09 Sep 2023
    date_str = re.sub(r'(\d{2})-(\w+)-(\d{2})', r'\1 \2 20\3', date_str)  # 09-Sep-23 -> 09 Sep 2023
    date_str = re.sub(r'(\w+)-(\d{2})-(\d{4})', r'\2 \1 \3', date_str)  # Aug-24-1806 -> 24 Aug 1806
    
    # Handle year ranges (e.g., 1900-1905)
    date_str = re.sub(r'(\d{4})-(\d{4})', lambda m: f'01 Jan {(int(m.group(1)) + int(m.group(2))) // 2}', date_str)  # 1900-1905 -> 1902
    
    # Handle dates with only year (e.g., 1900)
    if re.match(r'^\d{4}$', date_str):
        date_str = f'01 Jan {date_str}'  # Convert to 01 Jan 1900
    
    # Handle dates with month and year (e.g., Jan 1900)
    if re.match(r'^\w+ \d{4}$', date_str):
        date_str = f'01 {date_str}'  # Convert to 01 Jan 1900
    
    # Handle dates with month and year in different format (e.g., Sep-1805)
    if re.match(r'^\w+-\d{4}$', date_str):
        date_str = f'01 {date_str.replace("-", " ")}'  # Convert to 01 Sep 1805
    
    # Handle dates with month name and year (e.g., October 1815)
    if re.match(r'^\w+ \d{4}$', date_str):
        date_str = f'01 {date_str}'  # Convert to 01 October 1815
    
    # Handle dates with "or" (e.g., 1990 or 1991)
    if re.match(r'^\d{4} or \d{4}$', date_str):
        date_str = date_str.split(' or ')[0]  # Take the first year
    
    # Handle dates with "B.C." (e.g., Ca. 214 B.C.)
    date_str = re.sub(r'B\.C\.', 'BC', date_str, flags=re.IGNORECASE)
    
    # Handle dates with "A.D." (e.g., Ca. 77 A.D.)
    date_str = re.sub(r'A\.D\.', 'AD', date_str, flags=re.IGNORECASE)
    
    # Handle dates with "Circa" or "Ca." (e.g., Circa 1855)
    date_str = re.sub(r'Circa|circa', '', date_str).strip()
    
    # Specific cases mapping
    specific_cases = {
        r'Before (\d{4})': lambda m: f'01 Jan {int(m.group(1)) - 1}',
        r'Before (\d{2})-(\w+)-(\d{4})': lambda m: f'{int(m.group(1)) - 1} {m.group(2)} {m.group(3)}',
        r'Between (\d{4}) & (\d{4})': lambda m: f'01 Jan {(int(m.group(1)) + int(m.group(2))) // 2}'
    }
    
    # Apply specific cases
    for pattern, func in specific_cases.items():
        date_str = re.sub(pattern, func, date_str)
    
    return date_str

def date_clean(df): 
    df['Date'] = df['Date'].apply(clean_date)
    return df 


#Type column 

def type_column(df): 
    
    # Step 1: Remove leading/trailing spaces
    df['Type'] = df['Type'].str.strip()
    
    # Step 2: Replace '?' and 'nan' with 'Unknown'
    df['Type'] = df['Type'].replace(['?', 'nan'], 'Unknown')
    
    # Step 3: Remplace 'Questionable', 'Unconfirmed', 'Invalid', 'Under investigation' with 'Unverified'
    
    df['Type'] = df['Type'].replace(['Questionable', 'Unverified', 'Invalid','Under investigation'], 'Unconfirmed')
    
    return df

def clean_country(country):
    if pd.isna(country):
        return country
    
    # Strip leading and trailing whitespace
    country = country.strip()
    
    # Convert to title case
    country = country.title()
    
    # Remove special characters
    country = re.sub(r'[^\w\s]', '', country)
    
    return country

def country_cleaned(df): 
    
    df['Country'] = df['Country'].apply(clean_country)
    
    return df




def state_cleaned(df): 
    
    df['State'] = df['State'].apply(clean_country)
    
    return df