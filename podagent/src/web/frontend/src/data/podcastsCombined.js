import summary1 from "./output1_1.json"
import summary2 from "./output1_2.json"
import summary3 from "./output1_3.json"
import a1 from "./output2_1.json"
import a2 from "./output2_2.json"
import a3 from "./output2_3.json"
import b1 from "./output3_1.json"
import b2 from "./output3_2.json"
import b3 from "./output3_3.json"
import transcriptAdam from "./transcripts/adam-frank.txt?raw"
import transcriptAndrew from "./transcripts/andrew-callaghan.txt?raw"
import transcriptAnnie from "./transcripts/annie-jacobsen.txt?raw"

const byId = {
  [summary1.episode_id]: {
    title: "Adam Frank Alien Civilizations and the Search for Extraterrestrial Life",
    host: "Lex Fridman",
    date: "2024-12-23",
    duration: "3h 26m",
    tags: Array.from(
      new Set([...(summary1.keywords || []), ...(summary2.keywords || []), ...(summary3.keywords || [])]),
    ),
    summaries: {
      "GPT-3.5": summary1,
      "Llama3-8B": summary2,
      "Llama3-8B (Fine-tuned)": summary3,
    },
    transcript: transcriptAdam || "",
  },
  [a1.episode_id]: {
    title: "Andrew Callaghan on Lex Fridman",
    host: "Lex Fridman",
    date: "2024-04-13",
    duration: "2h 52m",
    tags: Array.from(new Set([...(a1.keywords || []), ...(a2.keywords || []), ...(a3.keywords || [])])),
    summaries: {
      "GPT-3.5": a1,
      "Llama3-8B": a2,
      "Llama3-8B (Fine-tuned)": a3,
    },
    transcript: transcriptAndrew || "",
  },
}

const annieId = b1.episode_id || b2.episode_id || b3.episode_id
if (annieId) {
  byId[annieId] = {
    title: "Annie Jacobsen Nuclear War, CIA, KGB, Aliens, Area 51, Roswell & Secrecy",
    host: "Lex Fridman",
    date: "2024-03-23",
    duration: "3h 07m",
    tags: Array.from(
      new Set([...(b1.keywords || []), ...(b2.keywords || []), ...(b3.keywords || [])]),
    ),
    summaries: {
      "GPT-3.5": b1,
      "Llama3-8B": b2,
      "Llama3-8B (Fine-tuned)": b3,
    },
    transcript: transcriptAnnie || "",
  }
}

export default byId
