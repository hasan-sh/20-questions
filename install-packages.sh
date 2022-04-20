# install all needed packages
echo "You are in a working virtualenv $VIRTUAL_ENV";
echo "Installing packages..";
pip install numpy SPARQLWrapper 
pip install wikipedia-api spacy transformers sentence_transformers pytest
# pip3 uninstall torch torchvision torchaudio #--extra-index-url https://download.pytorch.org/whl/cu113
python3 -m spacy download en_core_web_lg
pip install git+https://github.com/thunlp/OpenNRE
echo "Done!"
echo "Tip: run 'python play.py' to start your first game!"
exit 0;