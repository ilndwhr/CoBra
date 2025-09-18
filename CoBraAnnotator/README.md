# CoBraAnnotator



This tool provides a lightweight GUI for annotating and editing three-constituent German compounds in CoNLL-U Format developed along the CoBra-resource.

It is designed to extend the Universal Dependencies (UD) format with new multiword-token spans for German multi-constituent compounds (similar to MWTs but on compond-constituent-level).





## Features



Load a .conllu parsed sentence into a text box. Enter the start token ID of the detected compound and the number of constituents. The tool automatically generates an input mask for a multiword token compound (span line) with the correct ID range, prefilled from the original token line. The mask displays empty entry fields for each constituent with all 10 CoNLL-U columns, so you can enter any parsing information manually.



On integration:



The annotator inserts the annotated span line and constituent lines into the sentence from the input text field, while keeping user-entered IDs and heads exactly as entered. It updates subsequent token IDs and heads only after the inserted span according to the selected number of constituents. There is an Option to clear all fields and resetting defaults (start ID=0, constituents=3, renumbering=on) after a completed annotation.The output window shows the annotated sentence, with a 'Copy to Clipboard'-button for easy insertion back into your dataset.





## Installation



Clone the repository and install requirements:



git clone 'link'

cd 'directory'

pip install -r requirements.txt



(Note: the necessary requirements usually come with standard Python installations on most systems. On Linux you may need to install python3-tk via your package manager.)





## Usage



To run the tool run the following line in terminal:



python conllu\_compound\_annotator.py





## User Manual



#### 1\. Load a Sentence



Paste a single .conllu-parsed sentence into the input text box at the top.



#### 2\. Select Compound Position



Enter the start token ID of the identified compound (Default: 5).



Enter the constituent count (Default: 3).



Click 'Load Fields'.



This will:



Create one span line (prefilled with the original token line, with ID range automatically calculated).



Create empty entry lines for each constituent (with 10 CoNLL-U columns).



Pre-fill the UPOS, XPOS and FEATS columns with the inherited annotations from the parent compound.



#### 3\. Annotate constituents



Fill in the fields for each constituent as desired (form, lemmas, POS tags, features, heads, etc.).



All fields are editable an will generate a warning message if left empty.



#### 4\. Integrate



Click 'Apply and integrate' to insert the annotated span and constituent lines into the input sentence.



Subsequent token and head IDs will be updated automatically.



The annotated sentence will appear in the output box.



#### 5\. Copy



Click 'Copy to Clipboard' to paste the annotated sentence into your main annotation file.



#### 6\. Clear



Click Clear to reset everything, including defaults (start ID = 0, count = 3, renumbering = on).

