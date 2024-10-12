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
    df.drop(columns=["Unnamed: 11"], inplace=True)
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



def clean_and_normalize_species(df, column_name):
    """
    Limpia y normaliza la columna de especies en el DataFrame.
    
    Args:
    df (pd.DataFrame): El DataFrame que contiene la columna a limpiar.
    column_name (str): El nombre de la columna a limpiar.
    
    Returns:
    pd.DataFrame: El DataFrame con la columna limpiada y normalizada.
    """
    def replace_species(value, replacements):
        if pd.notna(value):  # Check if value is not NaN
            value_lower = value.lower()
            for key, replacement in replacements.items():
                if key in value_lower:
                    return replacement
        return value

    # Diccionario de términos y sus sustituciones
    replacements = {
        'white': 'White Shark',
        'tiger': 'Tiger Shark',
        'bull': 'Bull Shark',
        'nurse': 'Nurse Shark',
        'blacktip': 'Blacktip Shark',
        'hammerhead': 'Hammerhead Shark',
        'lemon': 'Lemon Shark',
        'blue': 'Blue Shark',
        'brown': 'Brown Shark',
        'raggedtooth': 'Raggedtooth Shark',
        'bronze': 'Bronze Shark',
        'caribbean': 'Caribbean Shark',
        'mako': 'Mako Shark'
    }

    # Aplicar la función de sustitución a la columna 'Species'
    df[column_name] = df[column_name].apply(replace_species, replacements=replacements)

    # Reemplazar valores no deseados con 'NA'
    mapping = {
        ' ' : 'NA',
        'no shark involvement' : 'NA',
        'no shark invovlement' : 'NA',
        'no shark invovlement - it ws a publicity stunt' : 'NA',
        'Invalid' : 'NA',
        'Invalid incident' : 'NA',
        'Questionable' :'NA',
        'Questionable incident' :'NA',
        '"small sharks"' : 'NA',
        '"a small shark"' : 'NA',
        'No shark involvement' : 'NA',
        '1NAm NA] shark' : 'NA',
        'Shark involvement prior to death was not confirmed' : 'NA',
        'Shark involvement not confirmed ' : 'NA',
        'NA shark ' : 'NA',
        '1NAm shark' : 'NA',
        "4' shark" : 'NA',
        "6' shark" : 'NA',
        "4' toNA shark" : 'NA',
        "2NAm NA] shark" : 'NA',
        "3' shark" : 'NA',
        "5' shark" : 'NA', 
        "3' toNA shark" : 'NA',
        "2 m shark" : 'NA',
        "3 m NA'] shark": 'NA',
        "3 m shark": 'NA', 
        "1NAm toNA5 m NA toNA] shark": 'NA',
        "3NAm NA'] shark": 'NA',
        "7' shark": 'NA', 
        "8' shark": 'NA',
        "5' toNA shark": 'NA',
        "2NAm shark": 'NA',
        "2' toNA shark": 'NA',
        "a small shark": 'NA',
        "Shark involvement prior to death not confirmed": 'NA',
        "1 m shark": 'NA',   
        "Shark involvement not confirmed": 'NA',
        "Shark involvement prior to death unconfirmed": 'NA',
        "NA shark": 'NA',
    }

    # Reemplazar valores no deseados en la columna 'Species'
    df[column_name] = df[column_name].replace(mapping)

    # Eliminar filas con 'NA' en la columna 'Species'
    df = df[df[column_name] != 'NA']
    
    return df




def add_oceans_column(df, country_column, new_column):
    """
    Añade una columna de océanos y mares al DataFrame basada en el país.
    
    Args:
    df (pd.DataFrame): El DataFrame que contiene la columna de países.
    country_column (str): El nombre de la columna de países.
    new_column (str): El nombre de la nueva columna a añadir.
    
    Returns:
    pd.DataFrame: El DataFrame con la nueva columna añadida.
    """
    countries_oceans = {
        'morocco': 'Atlantic Ocean',
        'jamaica': 'Caribbean Sea',
        'belize': 'Caribbean Sea',
        'australia': 'Indian Ocean and Pacific Ocean',
        'usa': 'Atlantic Ocean and Pacific Ocean',
        'maldive islands': 'Indian Ocean',
        'turks and caicos': 'Atlantic Ocean',
        'french polynesia': 'Pacific Ocean',
        'tobago': 'Caribbean Sea',
        'bahamas': 'Atlantic Ocean',
        'india': 'Indian Ocean',
        'trinidad': 'Caribbean Sea',
        'south africa': 'Atlantic Ocean and Indian Ocean',
        'mexico': 'Pacific Ocean and Gulf of Mexico',
        'new zealand': 'Pacific Ocean',
        'egypt': 'Red Sea',
        'spain': 'Atlantic Ocean and Mediterranean Sea',
        'portugal': 'Atlantic Ocean',
        'samoa': 'Pacific Ocean',
        'colombia': 'Pacific Ocean and Caribbean Sea',
        'ecuador': 'Pacific Ocean',
        'cuba': 'Caribbean Sea',
        'brazil': 'Atlantic Ocean',
        'seychelles': 'Indian Ocean',
        'new caledonia': 'Pacific Ocean',
        'argentina': 'Atlantic Ocean',
        'fiji': 'Pacific Ocean',
        'maldives': 'Indian Ocean',
        'england': 'Atlantic Ocean',
        'japan': 'Pacific Ocean',
        'indonesia': 'Indian Ocean and Pacific Ocean',
        'thailand': 'Indian Ocean and Andaman Sea',
        'costa rica': 'Pacific Ocean and Caribbean Sea',
        'canada': 'Atlantic Ocean, Pacific Ocean, and Arctic Ocean',
        'jordan': 'Red Sea',
        'papua new guinea': 'Pacific Ocean',
        'reunion island': 'Indian Ocean',
        'china': 'Pacific Ocean',
        'ireland': 'Atlantic Ocean',
        'italy': 'Mediterranean Sea',
        'malaysia': 'Indian Ocean and South China Sea',
        'mauritius': 'Indian Ocean',
        'solomon islands': 'Pacific Ocean',
        'united kingdom': 'Atlantic Ocean',
        'united arab emirates': 'Persian Gulf',
        'philippines': 'Pacific Ocean',
        'cape verde': 'Atlantic Ocean',
        'dominican republic': 'Caribbean Sea',
        'cayman islands': 'Caribbean Sea',
        'aruba': 'Caribbean Sea',
        'mozambique': 'Indian Ocean',
        'puerto rico': 'Caribbean Sea',
        'greece': 'Mediterranean Sea',
        'france': 'Atlantic Ocean and Mediterranean Sea',
        'kiribati': 'Pacific Ocean',
        'taiwan': 'Pacific Ocean',
        'guam': 'Pacific Ocean',
        'nigeria': 'Atlantic Ocean',
        'tonga': 'Pacific Ocean',
        'scotland': 'Atlantic Ocean',
        'croatia': 'Adriatic Sea',
        'saudi arabia': 'Red Sea and Persian Gulf',
        'chile': 'Pacific Ocean',
        'kenya': 'Indian Ocean',
        'russia': 'Arctic Ocean and Pacific Ocean',
        'south korea': 'Pacific Ocean',
        'malta': 'Mediterranean Sea',
        'vietnam': 'South China Sea',
        'madagascar': 'Indian Ocean',
        'panama': 'Pacific Ocean and Caribbean Sea',
        'somalia': 'Indian Ocean',
        'norway': 'Atlantic Ocean and Arctic Ocean',
        'senegal': 'Atlantic Ocean',
        'yemen': 'Red Sea and Gulf of Aden',
        'sri lanka': 'Indian Ocean',
        'uruguay': 'Atlantic Ocean',
        'micronesia': 'Pacific Ocean',
        'tanzania': 'Indian Ocean',
        'marshall islands': 'Pacific Ocean',
        'hong kong': 'Pacific Ocean',
        'el salvador': 'Pacific Ocean',
        'bermuda': 'Atlantic Ocean',
        'montenegro': 'Adriatic Sea',
        'iran': 'Persian Gulf and Caspian Sea',
        'tunisia': 'Mediterranean Sea',
        'namibia': 'Atlantic Ocean',
        'bangladesh': 'Bay of Bengal',
        'western samoa': 'Pacific Ocean',
        'palau': 'Pacific Ocean',
        'grenada': 'Caribbean Sea',
        'turkey': 'Mediterranean Sea and Black Sea',
        'singapore': 'Indian Ocean',
        'sudan': 'Red Sea',
        'nicaragua': 'Pacific Ocean and Caribbean Sea',
        'american samoa': 'Pacific Ocean',
        'guatemala': 'Pacific Ocean and Caribbean Sea',
        'netherlands antilles': 'Caribbean Sea',
        'iceland': 'Atlantic Ocean',
        'barbados': 'Caribbean Sea',
        'guyana': 'Atlantic Ocean',
        'haiti': 'Caribbean Sea',
        'kuwait': 'Persian Gulf',
        'cyprus': 'Mediterranean Sea',
        'lebanon': 'Mediterranean Sea',
        'martinique': 'Caribbean Sea',
        'paraguay': 'Landlocked',
        'peru': 'Pacific Ocean',
        'ghana': 'Atlantic Ocean',
        'greenland': 'Atlantic Ocean and Arctic Ocean',
        'sweden': 'Baltic Sea',
        'djibouti': 'Red Sea and Gulf of Aden'
    }

    # Convertir los nombres de los países a minúsculas y eliminar espacios adicionales
    df[country_column] = df[country_column].str.lower().str.strip()
    
    # Convertir las claves del diccionario a minúsculas y eliminar espacios adicionales
    countries_oceans = {k.lower().strip(): v for k, v in countries_oceans.items()}
    
    # Imprimir algunos valores intermedios para depuración
    print("Valores únicos de la columna de países después de convertir a minúsculas y eliminar espacios:")
    print(df[country_column].unique())
    
    df[new_column] = df[country_column].map(countries_oceans)
    
    # Imprimir algunos valores del DataFrame después de añadir la nueva columna
    print("Valores del DataFrame después de añadir la columna de océanos y mares:")
    print(df[[country_column, new_column]].head(20))
    
    return df
