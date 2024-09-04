import pandas as pd
from matplotlib import pyplot as plt

def open_glow_csv(fp) -> pd.Series:
    df = pd.read_csv(fp, parse_dates=['dateTime'], index_col='dateTime')
    return df['kWh']

GENERATION_MIX_COLUMNS = "GAS,COAL,NUCLEAR,WIND,HYDRO,IMPORTS,BIOMASS,OTHER,SOLAR,STORAGE".split(',')

def open_smart_meter():
    ''' open and import the smart meter data downloaded from glow/hildebrand'''
    df = pd.DataFrame({
        'imports': open_glow_csv('smart_meter.csv')
    })
    df.loc[df['imports'] > 15, 'imports'] = pd.NA # remove a handful of data errors/missing values
    df['imports'] = df['imports'].interpolate()
    return df

CARBON_INTENSITY_COL = 'CARBON_INTENSITY'
GRID_GENERATION_COL = 'GENERATION'

def open_grid():
    ''' open and import the grid carbon intensity and generation mix data downloaded from NGESO'''
    return pd.read_csv('grid.csv', parse_dates=['DATETIME'], index_col='DATETIME')

def carbon_mix():
    '''Calculate and plot my house carbon mix against the Grid average on a weekly basis'''
    df = open_smart_meter()
    
    grid = open_grid()
    
    # Ensure the grid data aligns with the home data's timestamps
    df = df.join(grid[[CARBON_INTENSITY_COL, GRID_GENERATION_COL]], how='inner')
    
    # Calculate carbon emissions for home imports and the grid
    df['home_carbon'] = df['imports'] * df[CARBON_INTENSITY_COL]
    df['grid_carbon'] = df[GRID_GENERATION_COL] * df[CARBON_INTENSITY_COL]
    
    # Calculate weekly total kWh and total carbon emissions for home and grid
    df_weekly = df.resample('W').sum()
    df_weekly['home_carbon_intensity'] = df_weekly['home_carbon'] / df_weekly['imports']
    df_weekly['grid_carbon_intensity'] = df_weekly['grid_carbon'] / df_weekly[GRID_GENERATION_COL]
    
    # Plot the weekly weighted average carbon intensity
    plt.figure(figsize=(12, 6.27))  # Set the figure size to 1200x627 pixels for LinkedIn
    plt.plot(df_weekly.index, df_weekly['home_carbon_intensity'], label='Home Carbon Intensity (g/kWh)', marker='o')
    plt.plot(df_weekly.index, df_weekly['grid_carbon_intensity'], label='Grid Carbon Intensity (g/kWh)', marker='o')
    
    # Add vertical lines for gas and petrol emissions
    plt.axhline(y=600, color='r', linestyle='--', label='Gas Boiler Equivalent (600 g/kWh)')
    plt.axhline(y=360, color='b', linestyle='--', label='Petrol ICE Car Equivalent (360 g/kWh)')
    
    plt.xlabel('Week')
    plt.ylabel('Carbon Intensity (g/kWh)')
    plt.title('Weekly Weighted Average Carbon Intensity')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # Save the plot as an image with the appropriate dimensions for LinkedIn
    plt.savefig('carbon_intensity_linkedin.png', dpi=100)
    
    # plt.show()
    # calculate the average carbon intensity for the home and grid
    home_avg = df['home_carbon'].sum() / df['imports'].sum()
    grid_avg = df['grid_carbon'].sum() / df[GRID_GENERATION_COL].sum()
    print(f'Home Average Carbon Intensity: {home_avg:.2f} g/kWh')
    print(f'Grid Average Carbon Intensity: {grid_avg:.2f} g/kWh')


def calculate_home_source_usage():
    df = open_smart_meter()
    grid = open_grid()

    # Assuming the grid mix is given in percentage
    grid_mix = grid[GENERATION_MIX_COLUMNS].div(grid[GENERATION_MIX_COLUMNS].sum(axis=1), axis=0)

    # Calculate the amount of each energy source used by the house
    for source in GENERATION_MIX_COLUMNS:
        df[source] = df['imports'] * grid_mix[source]

    # Resample to weekly data and sum
    weekly_usage = df[GENERATION_MIX_COLUMNS].resample('W').sum()

    return weekly_usage

def plot_stacked_area(weekly_usage):
   
    weekly_usage = weekly_usage[['NUCLEAR', 'GAS', 'WIND', 'IMPORTS', 'SOLAR', 'HYDRO', 'BIOMASS', 'OTHER', 'STORAGE', 'COAL']]
    
    plt.figure(figsize=(10, 6))

    # Plot the stacked area chart
    weekly_usage.plot.area()
    plt.title('Weekly Home Energy Source Usage')
    plt.ylabel('Energy Consumption (kWh)')
    plt.xlabel('Week')
    plt.legend(loc='upper left')
    plt.grid(True)
    plt.tight_layout()

    # Save the plot
    plt.savefig('home_energy_source_usage.png')
    plt.show()
    
def energy_sources():
    ''' plot and save the weekly energy source usage of the house'''
    weekly_usage = calculate_home_source_usage()
    plot_stacked_area(weekly_usage)


if __name__ == '__main__':
    carbon_mix()
    energy_sources()