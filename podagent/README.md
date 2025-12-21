PYTHONPATH=podagent/src python podagent/scripts/merge_output_into_podcasts.py \
  /Users/jaisharma/JAI_MB_SSD/Project/PodAgent/output.json \
  --podcasts-json /Users/jaisharma/JAI_MB_SSD/Project/PodAgent/podagent/src/web/frontend/src/data/podcasts.json \
  --podcast-key adam-frank-lex-fridman --model-label "GPT-3.5"




PYTHONPATH=podagent/src python podagent/scripts/summarize.py <episode_id> --mode openai --structured --output-json output.json

PYTHONPATH=podagent/src OPENAI_API_KEY=... \
python podagent/scripts/summarize.py <episode_id> \
  --mode openai --structured \
  --hierarchical --group-size 8 \
  --output-json output.json


PYTHONPATH=podagent/src OPENAI_API_KEY="$OPENAI_API_KEY" \
python podagent/scripts/summarize.py transcript-for-adam-frank-alien-civilizations-and-the-search-for-extraterrestrial-life-lex-fridman --mode openai --structured \
  --context-chunks 10000 --output-json output.json

# Episode 1 - adam-frank-alien-civilizations-and-the-search-for-extraterrestrial-life-lex-fridman

python podagent/scripts/summarize.py transcript-for-adam-frank-alien-civilizations-and-the-search-for-extraterrestrial-life-lex-fridman --mode openai --structured \
  --context-chunks 10000 --output-json output1_1.json

python podagent/scripts/summarize.py transcript-for-adam-frank-alien-civilizations-and-the-search-for-extraterrestrial-life-lex-fridman --mode together --structured \
  --hierarchical --group-size 30 --output-json output1_2.json

python podagent/scripts/summarize.py transcript-for-adam-frank-alien-civilizations-and-the-search-for-extraterrestrial-life-lex-fridman --mode together --structured --context-chunks 10000 --output-json output1_3.json

PYTHONPATH=podagent/src python podagent/scripts/merge_output_into_podcasts.py \
  /Users/jaisharma/JAI_MB_SSD/Project/PodAgent/output.json \
  --podcasts-json /Users/jaisharma/JAI_MB_SSD/Project/PodAgent/podagent/src/web/frontend/src/data/podcasts.json \
  --podcast-key adam-frank-lex-fridman --model-label "GPT-3.5"

  python podagent/scripts/summarize.py transcript-for-adam-frank-alien-civilizations-and-the-search-for-extraterrestrial-life-lex-fridman --mode together --structured \
  --hierarchical --group-size 30 \
  --intermediate-min-words 180 --intermediate-max-words 300 \
  --final-target-words 1000 --final-max-tokens 3000 \
  --output-json output.json

python podagent/scripts/summarize.py transcript-for-adam-frank-alien-civilizations-and-the-search-for-extraterrestrial-life-lex-fridman --mode together --structured \
  --context-chunks 200 \
  --final-target-words 1000 --final-max-tokens 3000 \
  --output-json output1_3.json


# Episode 2 - transcript-for-andrew-callaghan-channel-5-gonzo-qanon-o-block-politics-alex-jones-lex-fridman

python podagent/scripts/summarize.py transcript-for-andrew-callaghan-channel-5-gonzo-qanon-o-block-politics-alex-jones-lex-fridman \
  --mode openai --structured --output-json output2_1.json

python podagent/scripts/summarize.py transcript-for-andrew-callaghan-channel-5-gonzo-qanon-o-block-politics-alex-jones-lex-fridman --mode together --structured \
  --hierarchical --group-size 30 \
  --intermediate-min-words 180 --intermediate-max-words 300 \
  --final-target-words 1000 --final-max-tokens 3000 \
  --output-json output.json


  # Episode 3 transcript-for-annie-jacobsen-nuclear-war-cia-kgb-aliens-area-51-roswell-secrecy-lex-fridman

python podagent/scripts/summarize.py transcript-for-annie-jacobsen-nuclear-war-cia-kgb-aliens-area-51-roswell-secrecy-lex-fridman \
  --mode openai --structured --output-json output3_1.json

python podagent/scripts/summarize.py transcript-for-annie-jacobsen-nuclear-war-cia-kgb-aliens-area-51-roswell-secrecy-lex-fridman --mode together --structured \
  --hierarchical --group-size 30 \
  --intermediate-min-words 180 --intermediate-max-words 300 \
  --final-target-words 1000 --final-max-tokens 3000 \
  --output-json output3_2.json
