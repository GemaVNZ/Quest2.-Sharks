# eliminar columnas

import pandas as pd
import re
import datetime
import numpy as np

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

def sex_clean(df): 
    
    df['Sex'] = df['Sex'].replace([' M', 'M ', 'M x 2' ], 'M')
    df['Sex'] = df['Sex'].replace(['lli', 'N', '.' ], 'undefined')
    
    return df


# Age

def clean_age(df): 
    
    df["Age"] = df["Age"].replace(['Middle Age', '(adult)', '"middle-age"', '50s', 'adult','Middle age'], 50)
    df['Age'] = df["Age"].replace(['20/30','20s', '28 & 22',  "20's", '28 & 26', '28, 23 & 30', '21 & ?', '23 & 20','20?', 'mid-20s','21 or 26','18 to 22','? & 19','23 & 26','25 or 28','"young"','young','17 & 35','18 or 20'],25)
    df["Age"] = df['Age'].replace(['40s', '45 and 15', '9 & 60', '46 & 34'], 45)
    df["Age"] = df['Age'].replace(['teen', 'Teen','a minor','Teens','?    &   14', '13 or 14','7      &    31', '16 to 18','13 or 18', '12 or 13'], 15)
    df["Age"] = df["Age"].replace('Both 11', 11)
    df["Age"] = df['Age'].replace(['a minor', '18 months', '9 months'], 1)
    df["Age"] = df['Age'].replace(['Elderly', '>50', "60's", '60s'], 65)
    df["Age"] = df['Age'].replace(['9 or 10', '10 or 12', '7 or 8','9 & 60','8 or 10'], 10)
    df["Age"] = df['Age'].replace(['mid-30s', '33 & 26', '31 or 33', '36 & 23','30 or 36','21, 34,24 & 35','Ca. 33','33 & 37','32 & 30','37, 67, 35, 27,  ? & 27','30 & 32','33 or 37'], 33)
    
    df['Age'] = df['Age'].str.split(" ").str[0].apply(pd.to_numeric, errors = "coerce")
    
    
    return df


# Time 

def clean_time_format(time_str):
   
    # Convertir el valor a cadena de texto
    time_str = str(time_str)
    
    # Manejar valores como NaN, "Not stated", "?"
    if pd.isna(time_str) or 'Not' in time_str or '?' in time_str or time_str == '' or time_str == ' ' or time_str ==  '':
        return np.nan
    
    if ('not advised' in time_str.lower() or 'not stated' in time_str.lower()): 
        return np.nan
    elif ('early morning' in time_str.lower() or 'morning' in time_str.lower() or 'just before noon' in time_str.lower() or 'am' in time_str.lower() or 'a.m.' in time_str.lower()
        or 'late morning' in time_str.lower() or 'noon' in time_str.lower() or 'mid morning' in time_str.lower() or 'mid-morning' in time_str.lower()
        or 'Sometime between 06h00 & 08hoo' in time_str or 'Between 11h00 & 12h00' in time_str or 'Before 10h30' in time_str): 
        return 'Morning'
    elif ('afternoon' in time_str.lower() or '"midday"' in time_str.lower() or 'early afternoon' in time_str.lower() or 'after noon' in time_str.lower() or
        'mid afternoon' in time_str.lower() or 'daytime' in time_str.lower() or '"after lunch"' in time_str.lower() or 'midday' in time_str.lower() or 
        'before daybreak' in time_str.lower() or '>17h30' in time_str or '17h00 Sunset' in time_str or 'Shortly before 13h00' in time_str): 
        return 'Afternoon'
    elif ('night' in time_str.lower() or '"evening"' in time_str.lower() or 'late afternoon' in time_str.lower() or 'sunset' in time_str.lower() or 'midnight' in time_str.lower()
        or 'lunchtime' in time_str.lower() or 'just before sundown' in time_str.lower() or 'shortly after midnight' in time_str.lower() or 'after dusk' in time_str.lower()
        or 'dusk' in time_str.lower() or '"night"' in time_str.lower() or 'nightfall' in time_str.lower() or 'just before dawn' in time_str.lower() or
        'dark' in time_str.lower() or '"shortly before dusk"' in time_str.lower() or 'After dusk' in time_str.lower() or 'after midnight' in time_str.lower() or 
        '"Early evening"' in time_str.lower() or 'After 04h00' in time_str or 'Ship aban-doned at 03h10' in time_str or '30 minutes after 1992.07.08.a' in time_str): 
        return 'Night'
    
    else: 
        # Tratar casos con "hr", "h", etc. y eliminar caracteres extra
        time_str = time_str.lower().replace('hr', 'h').replace('hoo', 'h').replace('jh', 'h')
        time_str = re.sub(r'[^\dh]', '', time_str)  # Eliminar caracteres no numéricos y letras extrañas
        
        # Eliminar 'h' al inicio o dobles h's incorrectas (como 'h12h00')
        time_str = re.sub(r'^h', '', time_str)  # Eliminar 'h' al inicio
        time_str = re.sub(r'h+', 'h', time_str)  # Asegurar que solo haya una 'h'

        
        
        # Tratar números como 1600 o 16h15, convertir a "HH:MM"
        match = re.match(r'(\d{1,2})h(\d{1,2})?', time_str)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            return f'{hour:02d}:{minute:02d}'
        
        match_numeric = re.match(r'(\d{1,4})', time_str)
        if match_numeric:
            hour = int(match_numeric.group(1)[:2])
            minute = int(match_numeric.group(1)[2:]) if len(match_numeric.group(1)) > 2 else 0
            return f'{hour:02d}:{minute:02d}'
    
    return time_str


def categorize_time(cleaned_time):
    if pd.isna(cleaned_time):
        return np.nan
    if cleaned_time == 'Morning':
        return 'Morning'
    if cleaned_time == 'Afternoon':
        return 'Afternoon'
    if cleaned_time == 'Night':
        return 'Night'
    
    try:
        # Convertir a horas y minutos
        hour, minute = map(int, cleaned_time.split(':'))
        if 6 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 18:
            return 'Afternoon'
        else:
            return 'Night'
    except:
        return np.nan
    
    
def cleaned_time(df):
    
    df['Time'] = df['Time'].apply(clean_time_format)
    df['Time'] = df['Time'].replace('', np.nan)
    df['Time'] = df['Time'].apply(categorize_time)
    
    return df


def clean_location_column(df, column_name):

    def clean_location(location):
        if pd.isna(location):
            return None
        
        # Strip leading and trailing whitespace
        location = location.strip()
        
        # Convert to title case
        location = location.title()
        
        # Remove special characters (except commas and periods)
        location = re.sub(r'[^\w\s,\.]', '', location)
        
        return location
    
    df[column_name] = df[column_name].apply(clean_location)
    return df

def location_cleaned(df):
    df['Country'] = df['Country'].str.lower()
    return df



def clean_activity_column(df, column_name):

    def clean_activity(activity):
        if pd.isna(activity):
            return None
        
        # Strip leading and trailing whitespace
        activity = activity.strip()
        
        # Convert to title case
        activity = activity.title()
        
        # Remove special characters (except commas and periods)
        activity = re.sub(r'[^\w\s,\.]', '', activity)
        
        # Normalize common terms
        activity = activity.replace('Snorkelling', 'Snorkeling')
        activity = activity.replace('Boogie Boarding', 'Bodyboarding')
        activity = activity.replace('Stand-Up Paddleboarding', 'Stand-Up Paddleboarding')
        activity = activity.replace('Stand-Up Paddle Boarding', 'Stand-Up Paddleboarding')
        activity = activity.replace('Scuba Diving', 'Scuba Diving')
        activity = activity.replace('Free Diving', 'Freediving')
        activity = activity.replace('Spearfishing', 'Spearfishing')
        activity = activity.replace('Surfing', 'Surfing')
        activity = activity.replace('Swimming', 'Swimming')
        activity = activity.replace('Wading', 'Wading')
        activity = activity.replace('Fishing', 'Fishing')
        activity = activity.replace('Kayaking', 'Kayaking')
        activity = activity.replace('Paddle Boarding', 'Paddleboarding')
        activity = activity.replace('Body Boarding', 'Bodyboarding')
        
        return activity
    
    df[column_name] = df[column_name].apply(clean_activity)
    return df

def activity_cleaned(df):
    df['Activity'] = df['Activity'].str.lower()
    return df



def clean_injury_column(df, column_name):
    
    def clean_injury(injury):
        if pd.isna(injury):
            return None
        
        # Strip leading and trailing whitespace
        injury = injury.strip()
        
        # Convert to sentence case
        injury = injury.capitalize()
        
        # Remove special characters (except commas and periods)
        injury = re.sub(r'[^\w\s,]', '', injury)
        
        # Remove text after a period
        if '.' in injury:
            injury = injury.split('.')[0]
        
        return injury.strip()
    
    df[column_name] = df[column_name].apply(clean_injury)
    return df

def injury_cleaned(df):
    df['Injury'] = df['Injury'].str.lower()
    return df



def clean_species_column(df, column_name):

    def clean_species(species):
        if pd.isna(species):
            return None
        
        # Strip leading and trailing whitespace
        species = species.strip()
        
        # Convert to title case
        species = species.title()
        
        # Remove special characters (except commas and periods)
        species = re.sub(r'[^\w\s,]', '', species)
        
        # Normalize common terms
        species = species.replace('Great White', 'Great White Shark')
        species = species.replace('Tiger Shark', 'Tiger Shark')
        species = species.replace('Bull Shark', 'Bull Shark')
        species = species.replace('Blacktip Shark', 'Blacktip Shark')
        species = species.replace('White Shark', 'White Shark')
        species = species.replace('Reef Shark', 'Reef Shark')
        species = species.replace('Sandbar Shark', 'Sandbar Shark')
        species = species.replace('Lemon Shark', 'Lemon Shark')
        species = species.replace('Oceanic Whitetip Shark', 'Oceanic Whitetip Shark')
        species = species.replace('Bronze Whaler', 'Bronze Whaler Shark')
        species = species.replace('Nurse Shark', 'Nurse Shark')
        species = species.replace('Mako Shark', 'Mako Shark')
        species = species.replace('Blue Shark', 'Blue Shark')
        species = species.replace('Wobbegong Shark', 'Wobbegong Shark')
        species = species.replace('Sand Tiger Shark', 'Sand Tiger Shark')
        species = species.replace('Galapagos Shark', 'Galapagos Shark')
        species = species.replace('Cookiecutter Shark', 'Cookiecutter Shark')
        species = species.replace('Spinner Shark', 'Spinner Shark')
        species = species.replace('Hammerhead Shark', 'Hammerhead Shark')
        species = species.replace('Epaulette Shark', 'Epaulette Shark')
        species = species.replace('Tope Shark', 'Tope Shark')
        species = species.replace('Horn Shark', 'Horn Shark')
        species = species.replace('Whaler Shark', 'Whaler Shark')
        
        # Remove text inside brackets and parentheses
        species = re.sub(r'\[.*?\]', '', species)
        species = re.sub(r'\(.*?\)', '', species)
        
        return species.strip()
    
    df[column_name] = df[column_name].apply(clean_species)
    return df

def species_cleaned(df):
    df['Country'] = df['Country'].str.lower()
    return df

