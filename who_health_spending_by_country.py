import pandas as pd
import plotly.graph_objects as go
# import difflib # Uncomment if you need close match debugging later

# Read the Excel file with two header rows.
# Ensure the path 'who_health_spending_data.xlsx' is correct
try:
    df = pd.read_excel('who_health_spending_data.xlsx', header=[0, 1])

    # --- REVERTED COLUMN PROCESSING ---
    # Use the simpler logic from your original code that worked.
    # This assumes the first header row contains 'Countries', 'Indicators', and the year '2022'.
    original_columns = df.columns
    try:
        # This line just takes the first level of the MultiIndex
        df.columns = [col[0] for col in df.columns.values]
        print("Original MultiIndex columns:", original_columns)
        print("Processed columns (using first level only):", df.columns.tolist())
    except Exception as e:
        print(f"Error processing columns with original logic: {e}")
        print("Original MultiIndex columns were:", original_columns)
        exit()
    # --- END REVERTED COLUMN PROCESSING ---

except FileNotFoundError:
    print("Error: 'who_health_spending_data.xlsx' not found. Please ensure the file is in the correct directory.")
    exit()
except Exception as e:
    print(f"Error reading Excel file: {e}")
    print("Check if the file format is as expected (two header rows).")
    exit()


# Choose the year for plotting.
year = "2022" # Make sure this year exists as a column name AFTER processing

# Check if the year column exists after processing
if year not in df.columns:
    print(f"Error: Year '{year}' not found in the processed data columns.")
    print(f"Processed columns are: {df.columns.tolist()}")
    # Find available years (assuming they might be numeric strings in columns)
    available_years = [col for col in df.columns if isinstance(col, (str, int, float)) and str(col).isdigit()]
    if available_years:
        print(f"Available potential year columns found: {', '.join(map(str, available_years))}")
    else:
        print("Could not automatically detect potential year columns in the processed names.")
    exit()
else:
    print(f"Successfully found year column: '{year}'")


# Define spending categories with associated indicators.
# IMPORTANT: Ensure these indicator names match the column names AFTER processing
# Since we are likely taking only the first header row, the 'Indicators' column might just be 'Indicators'
categories = {
    "Taxation": [
         "Transfers from government domestic revenue (allocated to health purposes)",
         "Social insurance contributions"
    ],
    "Compulsory prepayment": [
         "Compulsory prepayment (Other, and unspecified, than FS.3)"
    ],
    "Voluntary Prepayment": [
         "Voluntary prepayment"
    ],
    "Fees/other": [
         "Other domestic revenues n.e.c.",
         "Unspecified revenues of health care financing schemes (n.e.c.)"
    ],
    "Foreign funding": [
         "Direct foreign transfers",
         "Transfers distributed by government from foreign origin"
    ]
}

# List of OECD members.
oecd_countries = [
    "Australia", "Austria", "Belgium", "Canada", "Chile", "Colombia", "Costa Rica",
    "Czechia", "Denmark", "Estonia", "Finland", "France", "Germany", "Greece",
    "Hungary", "Iceland", "Ireland", "Israel", "Italy", "Japan", "Republic of Korea", "Latvia",
    "Lithuania", "Luxembourg", "Mexico", "Netherlands", "New Zealand", "Norway",
    "Poland", "Portugal", "Slovakia", "Slovenia", "Spain", "Sweden",
    "Switzerland", "Türkiye", "UK", "USA"
]

# Pivot the data so that each country is a row with indicator values for the chosen year.
# The 'columns' argument here must match the name of the indicator column AFTER processing
# It's likely just 'Indicators' if the original logic worked
indicator_col_name = 'Indicators' # <--- ASSUMPTION: Check this matches df.columns
country_col_name = 'Countries'   # <--- ASSUMPTION: Check this matches df.columns

if indicator_col_name not in df.columns:
    print(f"Error: The assumed indicator column '{indicator_col_name}' not found in processed columns.")
    print(f"Processed columns: {df.columns.tolist()}")
    # Try to find a likely candidate
    possible_indicator_cols = [c for c in df.columns if 'indicator' in str(c).lower()]
    if possible_indicator_cols:
        print(f"Did you mean one of these: {possible_indicator_cols}?")
    exit()
if country_col_name not in df.columns:
    print(f"Error: The assumed country column '{country_col_name}' not found in processed columns.")
    print(f"Processed columns: {df.columns.tolist()}")
    exit()


try:
    # Use the assumed column names
    pivot_df = df.pivot(index=country_col_name, columns=indicator_col_name, values=year).fillna(0)
    print(f"\nPivoting successful using index='{country_col_name}', columns='{indicator_col_name}', values='{year}'.")
except KeyError as e:
     print(f"\nError during pivoting: {e}")
     print(f"Please check if '{country_col_name}', '{indicator_col_name}', and the year '{year}' columns exist and are correctly named after processing.")
     print(f"Processed columns: {df.columns.tolist()}")
     exit()
except Exception as e:
    print(f"\nAn unexpected error occurred during pivoting: {e}")
    exit()

actual_countries_in_data = set(pivot_df.index) # Use set for efficient lookup
missing_oecd_countries = []
for oecd_country in oecd_countries:
    if oecd_country not in actual_countries_in_data:
        missing_oecd_countries.append(oecd_country)

if missing_oecd_countries:
    print("\n--- ERROR: OECD Country Name Mismatch ---")
    print("The following countries listed in 'oecd_countries' were NOT found in the dataset's country list:")
    for country in missing_oecd_countries:
        print(f"- {country}")
    print("\nPlease check for spelling differences or variations in the country names.")
    exit()
else:
    print("\nAll specified OECD countries were found in the dataset.")

# Aggregate spending per category for each country.
cat_values = {}
print("\nChecking indicators in pivot table columns:")
pivot_cols = pivot_df.columns.tolist()
# print(f"Pivot columns: {pivot_cols}") # Uncomment for debugging column names
all_indicators_found = True
for cat, indicators in categories.items():
    valid_indicators = []
    for ind in indicators:
        if ind in pivot_cols:
            valid_indicators.append(ind)
        else:
             # This warning is more important now, as indicator names must match pivoted columns
             print(f"Warning: Indicator '{ind}' not found in pivoted data columns for category '{cat}'.")
             # Uncomment the lines below if you need help finding close matches
             # matches = difflib.get_close_matches(ind, pivot_cols, n=1, cutoff=0.8)
             # if matches:
             #     print(f"  -> Did you mean '{matches[0]}'?")
             # else:
             #     print(f"  -> No close match found in pivoted columns: {pivot_cols[:10]}...") # Show first few pivoted columns
             all_indicators_found = False


    if valid_indicators:
        cat_values[cat] = pivot_df[valid_indicators].sum(axis=1)
        # print(f"Category '{cat}': Found indicators {valid_indicators}") # Less verbose
    else:
        cat_values[cat] = pd.Series(0, index=pivot_df.index)
        print(f"Category '{cat}': No matching indicators found in pivoted data.")

if not all_indicators_found:
     print("\n*** Please check the indicator names in the 'categories' dictionary against the pivoted data columns listed above. ***\n")

# --- NEW: Calculate Total Spend ---
total_spend = pd.Series(0, index=pivot_df.index)
for cat in categories.keys():
    if cat in cat_values:
        total_spend += cat_values[cat]
print("Calculated total spend per country.")

# --- MODIFIED: Sort countries by BOTH Taxation and Total Spend ---
sort_category_taxation = "Taxation"

# Sorting by Taxation
if sort_category_taxation not in cat_values or cat_values[sort_category_taxation].sum() == 0:
    print(f"Warning: Sorting category '{sort_category_taxation}' has no data. Sorting by country name instead for Taxation sort.")
    countries_sorted_all_tax = sorted(pivot_df.index.tolist())
else:
    countries_sorted_all_tax = cat_values[sort_category_taxation].sort_values(ascending=False).index.tolist()
    print(f"Generated country list sorted by '{sort_category_taxation}'.")

# Sorting by Total Spend
if total_spend.sum() == 0:
     print(f"Warning: Total spend is zero for all countries. Sorting by country name instead for Total Spend sort.")
     countries_sorted_all_total = sorted(pivot_df.index.tolist())
else:
    countries_sorted_all_total = total_spend.sort_values(ascending=False).index.tolist()
    print("Generated country list sorted by Total Spend.")


# Create filtered sorted lists for OECD based on both sorting methods.
countries_sorted_oecd_tax = [country for country in countries_sorted_all_tax if country in oecd_countries]
countries_sorted_oecd_total = [country for country in countries_sorted_all_total if country in oecd_countries]


# Define an infographic-friendly colour palette.
colors = {
    "Taxation": "#1f77b4",  # blue
    "Compulsory prepayment": "#2ca02c",                 # green
    "Voluntary Prepayment": "#ff7f0e",                  # orange
    "Fees/other": "#9467bd",                            # purple
    "Foreign funding": "#8c564b"                        # brown
}

# --- MODIFIED: Prepare data for all FOUR views ---
category_keys = list(categories.keys()) # Get a fixed order of categories

data_all_tax = {}
data_oecd_tax = {}
data_all_total = {}
data_oecd_total = {}

for cat in category_keys:
    if cat in cat_values:
        # Data for Taxation Sort
        data_all_tax[cat] = {
            'x': list(countries_sorted_all_tax),
            'y': list(cat_values[cat].loc[countries_sorted_all_tax])
        }
        data_oecd_tax[cat] = {
            'x': list(countries_sorted_oecd_tax),
            'y': list(cat_values[cat].loc[countries_sorted_oecd_tax])
        }
        # Data for Total Sort
        data_all_total[cat] = {
            'x': list(countries_sorted_all_total),
            'y': list(cat_values[cat].loc[countries_sorted_all_total])
        }
        data_oecd_total[cat] = {
            'x': list(countries_sorted_oecd_total),
            'y': list(cat_values[cat].loc[countries_sorted_oecd_total])
        }
    else:
        # Handle case where category had no valid indicators
        print(f"Note: Category '{cat}' has no data; plots will show zero.")
        empty_y_all_tax = [0] * len(countries_sorted_all_tax)
        empty_y_oecd_tax = [0] * len(countries_sorted_oecd_tax)
        empty_y_all_total = [0] * len(countries_sorted_all_total)
        empty_y_oecd_total = [0] * len(countries_sorted_oecd_total)

        data_all_tax[cat] = {'x': list(countries_sorted_all_tax), 'y': empty_y_all_tax}
        data_oecd_tax[cat] = {'x': list(countries_sorted_oecd_tax), 'y': empty_y_oecd_tax}
        data_all_total[cat] = {'x': list(countries_sorted_all_total), 'y': empty_y_all_total}
        data_oecd_total[cat] = {'x': list(countries_sorted_oecd_total), 'y': empty_y_oecd_total}

# --- Pre-calculate lists and ranges for each view ---

# OECD, Sort by Taxation (Initial View)
oecd_tax_x_data = [data_oecd_tax[cat]['x'] for cat in category_keys if cat in data_oecd_tax]
oecd_tax_y_data = [data_oecd_tax[cat]['y'] for cat in category_keys if cat in data_oecd_tax]
oecd_tax_tick_vals = next((data_oecd_tax[cat]['x'] for cat in category_keys if cat in data_oecd_tax and data_oecd_tax[cat]['x']), [])
oecd_tax_range = [-0.5, len(oecd_tax_tick_vals) - 0.5] if oecd_tax_tick_vals else None
oecd_tax_tick_size = 16

# OECD, Sort by Total
oecd_total_x_data = [data_oecd_total[cat]['x'] for cat in category_keys if cat in data_oecd_total]
oecd_total_y_data = [data_oecd_total[cat]['y'] for cat in category_keys if cat in data_oecd_total]
oecd_total_tick_vals = next((data_oecd_total[cat]['x'] for cat in category_keys if cat in data_oecd_total and data_oecd_total[cat]['x']), [])
oecd_total_range = [-0.5, len(oecd_total_tick_vals) - 0.5] if oecd_total_tick_vals else None
oecd_total_tick_size = 16

# All, Sort by Taxation
all_tax_x_data = [data_all_tax[cat]['x'] for cat in category_keys if cat in data_all_tax]
all_tax_y_data = [data_all_tax[cat]['y'] for cat in category_keys if cat in data_all_tax]
all_tax_tick_vals = next((data_all_tax[cat]['x'] for cat in category_keys if cat in data_all_tax and data_all_tax[cat]['x']), [])
all_tax_range = [-0.5, len(all_tax_tick_vals) - 0.5] if all_tax_tick_vals else None
all_tax_tick_size = 6 

# All, Sort by Total
all_total_x_data = [data_all_total[cat]['x'] for cat in category_keys if cat in data_all_total]
all_total_y_data = [data_all_total[cat]['y'] for cat in category_keys if cat in data_all_total]
all_total_tick_vals = next((data_all_total[cat]['x'] for cat in category_keys if cat in data_all_total and data_all_total[cat]['x']), [])
all_total_range = [-0.5, len(all_total_tick_vals) - 0.5] if all_total_tick_vals else None
all_total_tick_size = 6 

# --- Create the stacked bar chart ---
fig = go.Figure()

# We add the traces in the same order as category_keys.
# Initial view: OECD, Sort by Taxation
for cat in category_keys:
    fig.add_trace(go.Bar(
        x=data_oecd_tax[cat]['x'], # Initial view: OECD, Tax sort
        y=data_oecd_tax[cat]['y'],
        name=cat,
        marker_color=colors.get(cat)
    ))

# Get the x-axis values for the initial (OECD, Tax Sort) view for ticks
initial_x_ticks = oecd_tax_tick_vals

# --- MODIFIED: Update layout with expanded dropdown menu ---
fig.update_layout(
    barmode='stack',
    title={
        'text': f'Source of health funding by country (% GDP, WHO data {year})', # Added units
        'x': 0.5, # Center title
        'xanchor': 'center',
        'font': {'family': 'Poppins, sans-serif', 'size': 24} # Slightly smaller title, add fallback font
    },
    xaxis=dict(
        tickvals=initial_x_ticks,
        ticktext=initial_x_ticks,
        tickangle=45,
        tickfont=dict(family='Poppins, sans-serif', size=oecd_tax_tick_size), # Initial size for OECD Tax sort
        title='', # No x-axis title
        range=oecd_tax_range # Set initial range
    ),
    yaxis=dict(
        title='% of GDP',
        title_font=dict(family='Poppins, sans-serif', size=18), # Adjust size
        tickfont=dict(family='Poppins, sans-serif', size=12) # Adjust size
    ),
    legend=dict(
        orientation="h", # Horizontal legend below plot
        yanchor="bottom",
        y=-0.20, # Adjust vertical position below x-axis labels (increased space)
        xanchor="center",
        x=0.5,
        bgcolor='rgba(255,255,255,0.5)',
        font=dict(family='Poppins, sans-serif', size=14), # Adjusted legend font size
        traceorder="normal"
    ),
    font=dict(family='Poppins, sans-serif'), # Default font for plot
    margin=dict(b=180), # Increase bottom margin further if labels/legend overlap
    updatemenus=[{
        'buttons': [
            {
                'method': 'update',
                'label': 'OECD (Sort: Taxation)',
                'args': [
                    {'x': oecd_tax_x_data, 'y': oecd_tax_y_data}, # Trace updates
                    { # Layout updates
                        'xaxis.tickfont.size': oecd_tax_tick_size,
                        'xaxis.tickvals': oecd_tax_tick_vals,
                        'xaxis.ticktext': oecd_tax_tick_vals,
                        'xaxis.range': oecd_tax_range,
                    }
                ],
            },
            {
                'method': 'update',
                'label': 'OECD (Sort: Total)',
                'args': [
                     {'x': oecd_total_x_data, 'y': oecd_total_y_data}, # Trace updates
                     { # Layout updates
                        'xaxis.tickfont.size': oecd_total_tick_size,
                        'xaxis.tickvals': oecd_total_tick_vals,
                        'xaxis.ticktext': oecd_total_tick_vals,
                        'xaxis.range': oecd_total_range,
                     }
                 ],
            },
            {
                'method': 'update',
                'label': 'All Countries (Sort: Taxation)',
                'args': [
                     {'x': all_tax_x_data, 'y': all_tax_y_data}, # Trace updates
                     { # Layout updates
                         'xaxis.tickfont.size': all_tax_tick_size,
                         'xaxis.tickvals': all_tax_tick_vals,
                         'xaxis.ticktext': all_tax_tick_vals,
                         'xaxis.range': all_tax_range,
                     }
                 ],
            },
            {
                 'method': 'update',
                 'label': 'All Countries (Sort: Total)',
                 'args': [
                     {'x': all_total_x_data, 'y': all_total_y_data}, # Trace updates
                     { # Layout updates
                         'xaxis.tickfont.size': all_total_tick_size,
                         'xaxis.tickvals': all_total_tick_vals,
                         'xaxis.ticktext': all_total_tick_vals,
                         'xaxis.range': all_total_range,
                     }
                 ],
            }
        ],
        'direction': 'down',
        'showactive': True,
        'x': 0.01, # Position menu slightly right
        'xanchor': 'left',
        'y': 1.1,  # Position menu slightly lower
        'yanchor': 'top'
    }]
)

# add logo
fig.update_layout(
    images=[{
        'source': "https://taxpolicy.org.uk/wp-content/assets/logo_standard.jpg",
        'xref': "paper",
        'yref': "paper",
        'x': 1,
        'y': 1,
        'sizex': 0.1,  # 10% of the screen width.
        'sizey': 0.1,
        'xanchor': "right",
        'yanchor': "top",
        'layer': "above"
    }]
)

# Add error handling for file writing
try:
    fig.write_html("who_health_spending_by_country.html")
    print("\nSuccessfully generated 'who_health_spending_by_country_sortable.html'")
except Exception as e:
    print(f"\nError writing HTML file: {e}")

# Optional: Show the figure if running interactively
# fig.show()