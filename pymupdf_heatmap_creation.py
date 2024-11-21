import pymupdf
import pandas as pd
import numpy as np
import matplotlib
import seaborn


import fitz  # PyMuPDF
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
import logging
from pathlib import Path
import re


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_positions_from_pdf(pdf_path, page_number=2):
    """
    Extract Northwestern player positions accurately from the left or right field of the PDF.
    """
    try:
        doc = fitz.open(pdf_path)
        page = doc[page_number]

        # Get page dimensions and midpoint
        width = page.rect.width
        height = page.rect.height
        mid_x = width / 2

        # Check Northwestern's side based on text
        text_page = page.get_text("dict")
        northwestern_on_left = None
        for block in text_page["blocks"]:
            if "Northwestern Wildcats" in str(block):
                block_center = (block["bbox"][0] + block["bbox"][2]) / 2
                northwestern_on_left = block_center < mid_x
                break

        if northwestern_on_left is None:
            raise ValueError("Unable to determine Northwestern's side from the PDF headers.")

        # Initialize positions
        positions = []

        # [i for i in text_page["block"] if 'Wildcat' in i['text']]

        temp = [i for i in text_page["blocks"] if "lines" in i]

        nu_elem = [i for i in temp if 'Wildcat' in i['lines'][0]['spans'][0]['text']][0]

        nu_elem_index = text_page['blocks'].index(nu_elem)

        rest = [i for i in text_page["blocks"] if "lines" in i][nu_elem_index:]

        dist_elem = [i for i in rest if ' m' in i['lines'][0]['spans'][0]['text']][0]

        dist_elem_index = text_page['blocks'].index(dist_elem)




        print('hello')


        # Process text blocks in the Northwestern field only
        for block in text_page["blocks"][nu_elem_index:dist_elem_index]:
            block_center = (block["bbox"][0] + block["bbox"][2]) / 2
            is_on_correct_side = (block_center < mid_x) if northwestern_on_left else (block_center > mid_x)

            if is_on_correct_side:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span["text"].strip()
                        if text.isdigit():  # Extract player positions based on numbers
                            x = (span["bbox"][0] + span["bbox"][2]) / 2
                            y = (span["bbox"][1] + span["bbox"][3]) / 2

                            # Normalize to field dimensions (68m x 108m for NCAA fields)
                            if northwestern_on_left:
                                x_norm = (x / mid_x) * 70
                            else:
                                x_norm = ((x - mid_x) / mid_x) * 70
                            y_norm = (1 - (y / (0.555*height))) * 150
                            positions.append((x_norm, y_norm))

        doc.close()
        return positions
    except Exception as e:
        logger.error(f"Error processing {pdf_path}: {str(e)}")
        return []


def create_heatmap(positions, title="Player Positions Heatmap", show_points=True):
    """
    Create a heatmap with NCAA soccer field dimensions (68m x 108m).
    """
    fig, ax = plt.subplots(figsize=(12, 8))  # Adjust proportions

    field_width = 68  # Field width in meters (NCAA average)
    field_length = 108  # Field length in meters (NCAA average)

    if len(positions) > 0:
        x = np.array([p[0] for p in positions])
        y = np.array([p[1] for p in positions])

        # Create heatmap
        sns.kdeplot(
            x=x, y=y, cmap='YlOrRd', fill=True, alpha=0.5, levels=15, bw_adjust=0.5, ax=ax
        )

        if show_points:
            ax.scatter(x, y, c='white', s=50, alpha=0.6, edgecolor='black')

    # Draw soccer field
    ax.set_facecolor('#1a472a')

    # Field outline
    ax.add_patch(Rectangle((0, 0), field_width, field_length, fill=False, color='white'))

    # Halfway line
    plt.plot([0, field_width], [field_length / 2, field_length / 2], 'white')

    # Center circle
    center_circle = plt.Circle((field_width / 2, field_length / 2), 9.15, fill=False, color='white')  # 9.15m radius
    ax.add_patch(center_circle)

    # Penalty areas
    penalty_area_width = 40.3
    penalty_area_length = 16.5
    ax.add_patch(Rectangle((field_width / 2 - penalty_area_width / 2, 0),
                           penalty_area_width, penalty_area_length,
                           fill=False, color='white'))
    ax.add_patch(Rectangle((field_width / 2 - penalty_area_width / 2, field_length - penalty_area_length),
                           penalty_area_width, penalty_area_length,
                           fill=False, color='white'))

    # Goal areas
    goal_area_width = 18.32  # Standard goal width in NCAA fields
    goal_area_length = 5.5
    ax.add_patch(Rectangle((field_width / 2 - goal_area_width / 2, 0),
                           goal_area_width, goal_area_length,
                           fill=False, color='white'))
    ax.add_patch(Rectangle((field_width / 2 - goal_area_width / 2, field_length - goal_area_length),
                           goal_area_width, goal_area_length,
                           fill=False, color='white'))

    plt.title(title, color='white', pad=20)
    plt.xlabel('Width (m)', color='white')
    plt.ylabel('Length (m)', color='white')

    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('white')

    ax.set_xlim(0, field_width)
    ax.set_ylim(0, field_length)
    ax.set_aspect('equal')
    return fig, ax

def find_folder(folder_name):
    """
    Recursively search for a folder starting from current directory.
    """
    for path in Path.cwd().rglob(folder_name):
        if path.is_dir():
            return path
    return None

def analyze_northwestern_games():
    """
    Analyze Northwestern's games and create visualizations.
    """
    base_dir = find_folder('northwestern-2024')
    
    if base_dir is None:
        print("\nError: Could not find 'northwestern-2024' folder.")
        print("Please ensure the folder exists somewhere in or below the current directory.")
        return

    print("\nStarting analysis...")
    print(f"Found folder at: {base_dir}")

    pdf_files = list(Path(base_dir).glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in the northwestern-2024 folder.")
        return
        
    output_dir = Path(base_dir) / 'heatmaps'
    output_dir.mkdir(exist_ok=True)

    for pdf_file in pdf_files:
        positions = extract_positions_from_pdf(pdf_file)
        if positions:
            fig, ax = create_heatmap(
                positions,
                title=f"Heatmap: {pdf_file.stem}",
                show_points=True
            )
            fig.savefig(
                output_dir / f"heatmap_{pdf_file.stem}.png",
                bbox_inches='tight',
                facecolor='#1a472a',
                edgecolor='none',
                dpi=300
            )
            plt.close(fig)
    print("\nAnalysis complete! Check the 'heatmaps' folder for output files.")

if __name__ == "__main__":
    analyze_northwestern_games()
