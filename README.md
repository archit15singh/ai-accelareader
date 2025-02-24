# ai-accelareader
accelerated learning of any book using AI and anki flashcards

### commands

python3.11 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt


marker_single ./books/1_effective_python.pdf --output_format markdown --output_dir ./markdown_output
marker_single ./books/1_python_tricks.pdf --output_format markdown --output_dir ./markdown_output
marker_single ./books/2_python_oops.pdf --output_format markdown --output_dir ./markdown_output
marker_single ./books/3_python_cookbook.pdf --output_format markdown --output_dir ./markdown_output
marker_single ./books/4_fluent_python.pdf --output_format markdown --output_dir ./markdown_output
