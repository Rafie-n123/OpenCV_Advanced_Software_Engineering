import re
import sys
from collections import Counter
import matplotlib.pyplot as plt

def parse_cluster_file(text):
    """
    Parses the cluster text and extracts statistics
    """
    lines = text.strip().split('\n')
    
    # First line as title
    title = lines[0] if lines else "Unknown Cluster"
    
    # Counters for statistics
    category_counter = Counter()
    subcategory_counter = Counter()
    
    # Process each line (except the first)
    for line in lines[1:]:
        # Find "opencv" in the path
        opencv_match = re.search(r'/opencv/', line)
        if not opencv_match:
            continue
        
        # Extract the part after "opencv/"
        after_opencv = line[opencv_match.end():]
        
        # Split by "/"
        path_parts = after_opencv.split('/')
        
        if len(path_parts) < 1:
            continue
        
        # First category after opencv (modules, 3rdparty, hal, build, apps, etc.)
        category = path_parts[0]
        category_counter[category] += 1
        
        # If it's modules, 3rdparty or hal, count the next level
        if category in ['modules', '3rdparty', 'hal'] and len(path_parts) > 1:
            subcategory = path_parts[1]
            subcategory_counter[subcategory] += 1
    
    return title, category_counter, subcategory_counter


def create_histograms(title, category_counter, subcategory_counter):
    """
    Creates two histograms for the statistics
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    fig.suptitle(title, fontsize=16, fontweight='bold')
    
    # Histogram 1: Main categories (modules, 3rdparty, hal, etc.)
    if category_counter:
        categories = list(category_counter.keys())
        counts = list(category_counter.values())
        
        ax1.bar(categories, counts, color='steelblue', edgecolor='black')
        ax1.set_xlabel('Category after opencv/', fontsize=12)
        ax1.set_ylabel('Count', fontsize=12)
        ax1.set_title('Distribution of Main Categories', fontsize=14)
        ax1.grid(axis='y', alpha=0.3)
        
        # Rotate labels if many categories
        if len(categories) > 5:
            ax1.tick_params(axis='x', rotation=45)
        
        # Show values on bars
        for i, (cat, count) in enumerate(zip(categories, counts)):
            ax1.text(i, count, str(count), ha='center', va='bottom')
    
    # Histogram 2: Subcategories (after modules/3rdparty/hal)
    if subcategory_counter:
        # Sort by frequency (Top 20)
        top_subcats = subcategory_counter.most_common(20)
        subcategories = [item[0] for item in top_subcats]
        subcounts = [item[1] for item in top_subcats]
        
        ax2.barh(subcategories, subcounts, color='coral', edgecolor='black')
        ax2.set_xlabel('Count', fontsize=12)
        ax2.set_ylabel('Subcategory', fontsize=12)
        ax2.set_title('Top 20 Subcategories (after modules/3rdparty/hal)', fontsize=14)
        ax2.grid(axis='x', alpha=0.3)
        ax2.invert_yaxis()  # Highest on top
        
        # Show values next to bars
        for i, count in enumerate(subcounts):
            ax2.text(count, i, f' {count}', va='center')
    
    plt.tight_layout()
    return fig


def read_file(filename):
    """
    Reads text from a file
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)


# Main program
if __name__ == "__main__":
    # Check if filename was provided
    if len(sys.argv) < 2:
        print("Usage: python script.py <filename>")
        print("Example: python script.py cluster_data.txt")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    # Read file content
    cluster_text = read_file(filename)
    
    # Analyze the text
    title, category_counter, subcategory_counter = parse_cluster_file(cluster_text)
    
    # Output statistics
    print(f"Title: {title}")
    print(f"\nMain Categories:")
    for cat, count in category_counter.most_common():
        print(f"  {cat}: {count}")
    
    print(f"\nTop Subcategories:")
    for subcat, count in subcategory_counter.most_common(10):
        print(f"  {subcat}: {count}")
    
    # Create histograms
    fig = create_histograms(title, category_counter, subcategory_counter)
    
    # Save figure to file
    output_filename = filename.rsplit('.', 1)[0] + '_histogram.png'
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"\nHistogram saved to: {output_filename}")
    
    plt.show()