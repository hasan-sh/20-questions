# install all needed packages
echo "You are in a working virtualenv $VIRTUAL_ENV";
echo "Installing packages..";
pip install numpy SPARQLWrapper 
echo "Done!"
echo "Tip: run 'python play.py' to start your first game!"
exit 0;