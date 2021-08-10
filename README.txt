README

1. Install dependencies using "pip3 install -r requirements.txt"
2. Download the medium sized spacy model using "python3 -m spacy download en_core_web_md"
3. The helper.py exists to support the main code with integrating to twitter and scoring the haikus
4. The main.py can be run in 2 modes : Twitter or Command line 

   If the twitter mode is chosen, the code will fetch the latest tweet from twitter and generate haiku for the movie tweeted. 
   Twitter does not allow duplicate tweets, so there can only be one tweet per movie.
   Run the code in twitter mode, and tweet @MovieSenryuBot in the following format to get a response:
   
   "@MovieSenryuBot movie_name"
   eg : @MovieSenryuBot Finding Nemo

   The command line mode expects the movie name to be enter in the command prompt and will print a haiku for the movie if it exists
   
   To run - "python3 main.py"