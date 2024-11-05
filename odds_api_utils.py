import requests
import pandas as pd

def fetch_data(api_key, sport, event_id=None, markets=None):
    """
    Fetch data from the odds API.
    
    Parameters:
        api_key (str): Your API key.
        sport (str): The sport key (e.g., 'americanfootball_nfl').
        event_id (str, optional): The event ID. If None, fetches general data for the sport.
        markets (str, optional): The markets you're interested in. If None, fetches all markets.

    Returns:
        DataFrame: A DataFrame containing the odds data, or None if there's an error.
    """
    base_url = 'https://api.the-odds-api.com'
    
    if event_id:
        url = f'{base_url}/v4/sports/{sport}/events/{event_id}/odds?apiKey={api_key}&regions=us'
    else:
        url = f'{base_url}/v4/sports/{sport}/odds?apiKey={api_key}&regions=us'
    
    if markets:
        url += f'&markets={markets}'
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return pd.DataFrame(data)
    else:
        print(f"Error: {response.status_code}")
        return None

def process_data(df):
    """
    Process the DataFrame returned from the API.
    
    Parameters:
        df (DataFrame): The DataFrame containing the odds data.

    Returns:
        DataFrame: A processed DataFrame.
    """
    df['key'] = df['bookmakers'].apply(lambda x: x['key'])
    df['title'] = df['bookmakers'].apply(lambda x: x['title'])
    df['markets'] = df['bookmakers'].apply(lambda x: x['markets'])

    df.drop(columns=['bookmakers'], inplace=True)
    df = df.explode('markets')

    # Extract key and last_update from markets
    df['market_key'] = df['markets'].apply(lambda x: x['key'])
    df['last_update'] = df['markets'].apply(lambda x: x['last_update'])

    # Keep the outcomes list
    df['outcomes'] = df['markets'].apply(lambda x: x['outcomes'])

    # Drop the original 'markets' column
    df.drop(columns=['markets'], inplace=True)
    df_exploded = df.explode('outcomes')
    
    def decimal_to_american(decimal_odds):
        if decimal_odds >= 2:
            return round((decimal_odds - 1) * 100)
        else:
            return round(-100 / (decimal_odds - 1))

    df_exploded['Odds'] = df_exploded['outcomes'].apply(lambda x: decimal_to_american(x['price']))
    df_exploded['OverUnder'] = df_exploded['outcomes'].apply(lambda x: x['name'])
    df_exploded['Player'] = df_exploded['outcomes'].apply(lambda x: x['description'])
    df_exploded['Line'] = df_exploded['outcomes'].apply(lambda x: x.get('point', ''))

    # Drop the original 'outcomes' column
    return df_exploded.drop(columns=['outcomes'])