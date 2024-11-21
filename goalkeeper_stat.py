import pandas as pd
import numpy as np
import re
import sys
import os
import matplotlib.pyplot as plt
import seaborn as sns

def nu_goalkeeper_stat(filepath):
    player = pd.read_csv(filepath)
    
    nu_player = player[(player['team']=='Northwestern Wildcats')
                   & (player['Position'].isin(['CB', 'LB', 'RB', 'RCB3', 'LCB3', 'FB', 'LWB', 'RWB', 'D', 'DM', 'GK']))]
    nu_player['Date'] = pd.to_datetime(nu_player['Date'])
    gk = nu_player[nu_player['Position']=='GK']
    
    # Get the Score
    gk['Score'] = gk['Match'].str.extract(r'(\d+:\d+)')

    columns = list(gk.columns)  # Get the list of column names
    columns.remove('Score')  # Remove 'Score' from the list
    match_index = columns.index('Match')  # Find the index of 'Match'
    columns.insert(match_index + 1, 'Score')  # Insert 'Score' after 'Match'

    gk = gk[columns]

    # Keywords to search for
    keywords = ['gk_stat','player_name','home_team','away_team','Competition','Date','year',
                'Minutes played','Match','Score']

    # Find columns matching any of the keywords
    matching_columns = gk.columns[gk.columns.str.contains('|'.join(keywords))]
    gk = gk[matching_columns]
    
    col = ['Minutes played','gk_stat_conceded_goals','gk_stat_xcg','gk_stat_shots_against','gk_stat_saves',
       'gk_stat_reflex_saves','gk_stat_box_exits','gk_stat_passes_to_gk','gk_stat_passes_to_gk_completed',
       'gk_stat_goal_kicks_attempted','gk_stat_short_goal_kicks','gk_stat_long_goal_kicks']
    res_gk = gk.groupby(['year','player_name','Competition'])[col].mean().round(2)
    
    # Exclude the 'Minutes played' column
    gk_stats = res_gk.drop(columns=['Minutes played','gk_stat_passes_to_gk','gk_stat_passes_to_gk_completed',
                                    'gk_stat_goal_kicks_attempted','gk_stat_short_goal_kicks','gk_stat_long_goal_kicks'])

    # Step 2: Ensure all data is numeric
    gk_stats = gk_stats.apply(pd.to_numeric, errors='coerce')

    # Step 3: Group the DataFrame by the MultiIndex levels
    grouped = gk_stats.groupby(level=['year', 'player_name','Competition'])

    # Step 4: Define the mapping dictionary
    rename_dict = {
        'gk_stat_conceded_goals': 'Conceded Goals',
        'gk_stat_xcg': 'Expected Goals Conceded',
        'gk_stat_shots_against': 'Shots Against',
        'gk_stat_saves': 'Saves',
        'gk_stat_reflex_saves': 'Reflex Saves',
        'gk_stat_box_exits': 'Box Exits'
    }

    # Step 1: Exclude 'Minutes played' and ensure numeric data
    gk_stats = res_gk.drop(columns=['Minutes played'])
    gk_stats = gk_stats.apply(pd.to_numeric, errors='coerce')

    # Step 2: Group the DataFrame by 'year' and 'player_name'
    grouped = gk_stats.groupby(level=['year', 'player_name'])

    # Step 3: Define the plotting function
    def plot_side_by_side_comparison(mean_bigten, mean_non_bigten, year, player_name, save=True):
        # Check if both competition types have data
        if mean_bigten.empty and mean_non_bigten.empty:
            print(f"Warning: No competition data for Year: {year}, Player: {player_name}. Skipping plot.")
            return
        elif mean_bigten.empty:
            print(f"Warning: 'Big Ten' data missing for Year: {year}, Player: {player_name}. Plotting only 'Non-Conference'.")
        elif mean_non_bigten.empty:
            print(f"Warning: 'Non-Conference' data missing for Year: {year}, Player: {player_name}. Plotting only 'Big Ten'.")
        
        # Create a combined DataFrame
        comparison_df = pd.DataFrame({
            'Big Ten': mean_bigten,
            'Non-Conference': mean_non_bigten
        })
        
        # Drop any statistics where both competition types are missing
        comparison_df = comparison_df.dropna(how='all')
        
        # Reset index to have 'Statistic' as a column
        comparison_df = comparison_df.reset_index()
        comparison_df.columns = ['Statistic', 'Big Ten', 'Non-Conference']
        
        # Melt the DataFrame for seaborn compatibility
        comparison_melted = comparison_df.melt(id_vars='Statistic', var_name='Competition', value_name='Mean Value')
        
        # Apply the renaming
        comparison_melted['Statistic'] = comparison_melted['Statistic'].map(rename_dict)
        
        # Handle any missing mappings
        if comparison_melted['Statistic'].isnull().any():
            missing = comparison_melted[comparison_melted['Statistic'].isnull()]['Statistic']
            print(f"Warning: The following statistics are missing in rename_dict and will retain their original names: {missing.tolist()}")
            comparison_melted['Statistic'].fillna(comparison_melted['Statistic'], inplace=True)
        
        # Initialize the matplotlib figure
        plt.figure(figsize=(14, 8))
        
        # Create the bar plot
        sns.barplot(
            data=comparison_melted,
            x='Statistic',
            y='Mean Value',
            hue='Competition',
            palette='viridis'
        )
        
        # Determine the maximum y-axis value
        current_max = comparison_melted['Mean Value'].max()
        y_max = max(5, current_max + 0.5)  # Adds a buffer of 0.5 above the highest bar
        
        # Set y-axis limits
        plt.ylim(0, y_max)  # Set y-axis from 0 to y_max
        
        # Add titles and labels
        plt.title(f"Mean Goalkeeper Statistics Comparison\nYear: {year}, Player: {player_name}", fontsize=18)
        plt.xlabel("GK Statistics", fontsize=16)
        plt.ylabel("Mean Value", fontsize=16)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        
        # Annotate each bar with its mean value
        for container in plt.gca().containers:
            plt.gca().bar_label(container, fmt='%.2f', padding=3)
        
        # Add gridlines for y-axis
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Adjust layout to prevent clipping of labels
        plt.tight_layout()
        
        # Display the plot
        plt.show()
        
        # Save the plot if required
        if save:
            # Create a filename-friendly string
            filename = f"mean_gk_stats_{year}_{player_name.replace(' ', '_')}.png"
            plt.savefig(filename, dpi=300)
            plt.close()  # Close the figure to free memory

    # Step 4: Iterate through each group and plot
    for (year, player_name), group in grouped:
        # Initialize empty Series for competition types
        mean_bigten = pd.Series(dtype='float64')
        mean_non_bigten = pd.Series(dtype='float64')
        
        # Attempt to extract Big Ten data
        try:
            bigten = group.xs('United States. NCAA D1 Big Ten', level='Competition')
            mean_bigten = bigten.mean()
        except KeyError:
            print(f"Warning: 'United States. NCAA D1 Big Ten' not found for Year: {year}, Player: {player_name}.")
        
        # Attempt to extract Non-Conference data
        try:
            non_conference = group.xs('United States. NCAA D1 Non-conference matches', level='Competition')
            mean_non_bigten = non_conference.mean()
        except KeyError:
            print(f"Warning: 'United States. NCAA D1 Non-conference matches' not found for Year: {year}, Player: {player_name}.")
        
        # Plot the side-by-side comparison if at least one competition type has data
        if not mean_bigten.empty or not mean_non_bigten.empty:
            plot_side_by_side_comparison(mean_bigten, mean_non_bigten, year, player_name, save=False)


