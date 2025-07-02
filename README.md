# DSF viewer

A simple streamlit application that can be accessed [here](https://dsf-viewer.streamlit.app/) which allows the analysis of Differential Scanning Fluorimetry data. It is a wrapper around (parts of) [the bada package](https://github.com/willigott/biophysical-assay-data-analysis).

## Known issues
- The code still needs significant improvements, e.e. there are plenty of code duplications, inconsistent naming and it's not yet leveraging all of `bada's` functionality (e.g. batch analysis of wells)
- there are no tests yet