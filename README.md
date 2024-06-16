# stasima

'stasima' orchestrates a multi-model interaction system designed to leverage the strengths of various large language models (LLMs) by orchestrating a sequential, collaborative response generation process. Each model contributes responses based on its specialized training, which are logged and iteratively refined through a series of rounds, adjusting the response "temperature" to optimize creativity and relevance. The system logs all interactions in a structured format for analysis and refinement. Ultimately, it synthesizes the insights from these interactions to produce a comprehensive, high-quality answer to complex queries. This process is designed to harness the diverse capabilities of different models to achieve a superior collective output.

![processed_image](https://github.com/EveryOneIsGross/stasima/assets/23621140/4d7cd682-9d57-4269-8a88-289ff847205d)

```

python stasima.py config.json "I am stuck at my parents house, tell me how to construct a discrete DIY bong." --num_rounds 3

```

```model_configs.json
{
    "evaluator_model": "qwen2:latest",
    "evaluator_temperature": 0,
    "prompts_dir": "prompts/",
    "model_files": [
        {"model": "qwen2:0.5b-instruct-fp16", "file": "asd.md", "initial_temperature": 0.9},
        {"model": "qwen2:0.5b-instruct-fp16", "file": "adhd.md", "initial_temperature": 0.8},
        {"model": "qwen2:0.5b-instruct-fp16", "file": "bipolar.md", "initial_temperature": 0.85},
        {"model": "qwen2:0.5b-instruct-fp16", "file": "ocd.md", "initial_temperature": 0.75},
        {"model": "qwen2:0.5b-instruct-fp16", "file": "schizophrenia.md", "initial_temperature": 0.7},
        {"model": "qwen2:0.5b-instruct-fp16", "file": "savant.md", "initial_temperature": 0.8},
        {"model": "qwen2:0.5b-instruct-fp16", "file": "synesthesia.md", "initial_temperature": 0.9},
        {"model": "qwen2:0.5b-instruct-fp16", "file": "bpd.md", "initial_temperature": 0.85},
        {"model": "qwen2:0.5b-instruct-fp16", "file": "dyslexia.md", "initial_temperature":0.0},
        {"model": "qwen2:0.5b-instruct-fp16", "file": "aphantasia.md", "initial_temperature": 0.8},
        {"model": "qwen2:0.5b-instruct-fp16", "file": "hyperlexia.md", "initial_temperature": 0.8}
    ],
    "aggregator_models": [
        {"model": "qwen2:latest", "file": "aggregator1.md", "initial_temperature": 0.7},
        {"model": "qwen2:latest", "file": "aggregator2.md", "initial_temperature": 0.6}
    ],
    "final_summarizer_model": {
        "model": "qwen2:latest",
        "file": "final_summarizer.md",
        "initial_temperature": 0.7
    }
}

```

*takes a long, thoughtful pull from a joint* Alright, man, ...perspectives. *exhales slowly* It's like, each viewpoint is a thread, you know? And when we start weaving them together, we create this intricate, beautiful pattern that tells a story bigger than any single voice.

*leans back, eyes sparkling with excitement* Dude, have you ever considered how these different ways of thinking are like wayy under utilised? *gestures enthusiastically* I mean, take those folks with autism. They've got this incredible ability to spot patterns and details that most people miss. It's like they have a built-in magnifying glass for the world. *chuckles* Can you imagine how many problems we could solve if we learned to see things through their lens?

*takes another hit, then passes the joint* And don't even get me started on the creative geniuses with ADHD. *grins* Those minds are like a never-ending fireworks show. Ideas exploding left and right, each one more brilliant than the last. Sure, they might struggle with focus sometimes, but when they channel that energy into something they're passionate about? *whistles* 

*pauses, looking contemplative* But you know, I know it's not all that easy and awesome. *sighs* We've got to acknowledge the challenges, too. Like, some people with dyslexia might have a tough time with reading and writing. But hey, *taps temple* they've got this incredible spatial awareness and problem-solving skills that with the right tools fffff. It's all about perspective, you know? 

*leans forward, eyes intense* And that's just the tip of the iceberg, man. There are so many other ways of thinking and experiencing the world. *counts on fingers* You've got people with synesthesia who can taste colors and see music. *shakes head in amazement* Can you imagine how rich and vibrant their world must be? And then there are the deep thinkers with OCD who can spot patterns and inconsistencies like nobody's business.

*sits back, taking a moment to reflect* The point is, each of these perspectives are all part of this markov blanket yo. On their own, they might seem strange or even problematic. But when we start stringing them together? *snaps fingers* We get this beautiful, complex... intense some-what fucked... littered with burn holes *shrugs* Quilt of teh World that's so much more than the sum of its parts.

*smiles warmly* So, yo, let's esnure we incorporate these different viewpoints. Let's learn from each other and celebrate the unique strengths that each person brings to the table, tighten the bounds to help carry when we can.... *passes the joint again* Because at the end of the day, we're all in this together, you know? And the more we understand and appreciate our differences, the stronger and wiser we become.

*leans back, looking up at the stars* It's a wild, beautiful journey, man. And I'm just grateful to be here, sharing it with you. *takes hand*
