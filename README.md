# Logo Clustering

A Python tool for finding clusters of visually similar logos based on shape similarity.

## Features

- Converts SVG logos to standardized black-and-white images
- Uses shape descriptors (Hu Moments and ORB) for similarity comparison
- Finds clusters of similar logos (minimum size: 3)
- Supports overlapping clusters
- Generates visual output of clusters
- Configurable similarity threshold

## Requirements

- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```bash
python logo_cluster.py --input-dir logos/ --output-dir clusters/ --threshold 0.85 --min-cluster-size 3
```

### Parameters

- `--input-dir`: Directory containing SVG logo files (default: "logos/")
- `--output-dir`: Directory for output files (default: "clusters/")
- `--threshold`: Similarity threshold (0.0 to 1.0, default: 0.85)
- `--min-cluster-size`: Minimum number of logos in a cluster (default: 3)

### Output

- Text file with cluster information
- Visual output showing each cluster as an image grid
- Log file with processing information

## Project Structure

```
.
├── logo_cluster.py      # Main script
├── svg_processor.py     # SVG to image conversion
├── shape_descriptor.py  # Shape feature extraction
├── similarity.py        # Similarity computation
├── clustering.py        # Cluster extraction
├── visualization.py     # Cluster visualization
├── utils.py            # Utility functions
├── requirements.txt    # Dependencies
└── README.md          # This file
```

## License

MIT License 