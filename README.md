# football_hackathon2024

This GitHub repository has the code to our project for the 2024 MLDS Hackathon. 

**Description:**


This project focuses on using Northwestern (and BIG 10) soccer match data to analyze and improve defensive structures. By utilizing data analytics, we aim to understand the defensive patterns that occured in wins vs losses, identify weaknesses, and propose potential improvements. The project uses both Python and R in order to create the necessary visualizations. 

**Before testing out python script:**
- Ensure to run `pip install -r requirements.txt`

`goalkeeper_stat.py`
- This script requires the usage of `player-combined-data.csv`.
- You will use `nu_goalkeeper_stat` to output the desired goalkeeper's bar chart stats.
- This will output bar charts of the Northwestern Wildcat Goalkeeper's stats.

`pymupdf_heatmap_creation.py`
- Thhis script extracts player (starters and subs) positions from a specific page of each PDF match report.
- Creates detailed heatmaps showing 1) player position density using a yellow-orange-red color scheme 2) full soccer field visualization including penalty areas, goal areas, and center circle 
- This will automatically save all generated heatmaps to a 'heatmaps' subfolder with game-specific filenames
