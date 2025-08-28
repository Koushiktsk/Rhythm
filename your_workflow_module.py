# your_workflow_module.py
from typing import TypedDict, Dict
from langgraph.graph import StateGraph, END
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import tempfile
import random
import music21

# Define your state
class MusicState(TypedDict):
    musician_input: str
    melody: str
    harmony: str
    rhythm: str
    style: str
    composition: str
    midi_file: str

# Initialize LLM
llm = ChatGroq(
    temperature=0,
    groq_api_key="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",  # Replace with your actual API key
    model_name="llama-3.3-70b-versatile"
)

# Define all your node functions (melody_generator, harmony_creator, etc.)
def melody_generator(state: MusicState) -> Dict:
    """Generate a melody based on user input using LLM"""
    prompt = ChatPromptTemplate.from_template(
        "You are an expert composer. Generate a melody based on this description: {input}. "
        "Represent it as a simple string of notes in ABC notation or music21 format. "
        "Example: 'C4 D4 E4 F4 G4' for a C major scale. Keep it to 8-16 notes."
    )
    chain = prompt | llm
    response = chain.invoke({"input": state["musician_input"]})

    # Extract just the note sequence from the LLM response
    melody_notes = response.content.strip()
    return {"melody": melody_notes}


def harmony_creator(state: MusicState) -> Dict:
    """Create harmony for the generated melody"""
    prompt = ChatPromptTemplate.from_template(
        "You are a music theory expert. Create chord progressions for this melody: {melody}. "
        "Suggest simple chord names in a progression. Example: 'C major, G major, A minor, F major'. "
        "Provide 4-8 chords that would work well with this melody."
    )
    chain = prompt | llm
    response = chain.invoke({"melody": state["melody"]})

    harmony_progression = response.content.strip()
    return {"harmony": harmony_progression}


def rhythm_analyzer(state: MusicState) -> Dict:
    """Analyze and suggest rhythm patterns"""
    prompt = ChatPromptTemplate.from_template(
        "You are a percussionist. Suggest rhythm patterns for this composition: "
        "Melody: {melody}, Harmony: {harmony}. "
        "Provide simple rhythm descriptions like '4/4 time, quarter notes for melody, whole notes for harmony' "
        "or 'waltz rhythm: 3/4 time, dotted half notes'."
    )
    chain = prompt | llm
    response = chain.invoke({
        "melody": state["melody"],
        "harmony": state["harmony"]
    })

    rhythm_pattern = response.content.strip()
    return {"rhythm": rhythm_pattern}


def style_adapter(state: MusicState) -> Dict:
    """Adapt the composition to the selected style"""
    prompt = ChatPromptTemplate.from_template(
        "You are a music style expert. Adapt this composition to {style} style: "
        "Melody: {melody}, Harmony: {harmony}, Rhythm: {rhythm}. "
        "Provide the final composition description in music21 format or simple instructions. "
        "Explain how you adapted it to the {style} style."
    )
    chain = prompt | llm
    response = chain.invoke({
        "style": state["style"],
        "melody": state["melody"],
        "harmony": state["harmony"],
        "rhythm": state["rhythm"]
    })

    adapted_composition = response.content.strip()
    return {"composition": adapted_composition}


def midi_converter(state: MusicState) -> Dict:
    """Convert the composition to MIDI format using music21"""
    try:
        # Create a new music21 stream
        stream = music21.stream.Stream()

        # Add the composition description as text
        description = music21.expressions.TextExpression(
            f"Composition: {state['composition']}\n"
            f"Style: {state['style']}\n"
            f"Original input: {state['musician_input']}"
        )
        stream.append(description)

        # Define scales and chords for different styles
        scales = {
            'Classical': {'C major': ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4']},
            'Romantic': {'C minor': ['C4', 'D4', 'Eb4', 'F4', 'G4', 'Ab4', 'Bb4']},
            'Jazz': {'C blues': ['C4', 'Eb4', 'F4', 'Gb4', 'G4', 'Bb4']},
            'Cinematic': {'C harmonic minor': ['C4', 'D4', 'Eb4', 'F4', 'G4', 'Ab4', 'B4']},
            'Electronic': {'C pentatonic': ['C4', 'D4', 'E4', 'G4', 'A4']},
        }

        chords = {
            'Classical': ['C major', 'G major', 'A minor', 'F major'],
            'Romantic': ['C minor', 'Ab major', 'F minor', 'G major'],
            'Jazz': ['C7', 'F7', 'G7', 'Dm7'],
            'Cinematic': ['C minor', 'Eb major', 'Ab major', 'Bb major'],
            'Electronic': ['C major', 'G major', 'A minor', 'E minor'],
        }

        # Get the appropriate scale and chords for the selected style
        style = state["style"]
        scale_name = list(scales.get(style, scales['Classical']).keys())[0]
        scale_notes = scales.get(style, scales['Classical'])[scale_name]
        style_chords = chords.get(style, chords['Classical'])

        # Create a simple melody based on the scale
        melody_part = music21.stream.Part()
        for i in range(16):  # 16 notes
            note_name = random.choice(scale_notes)
            note = music21.note.Note(note_name)
            note.quarterLength = random.choice([0.5, 1.0, 2.0])  # Varied note lengths
            melody_part.append(note)

        # Create harmony based on the chord progression
        harmony_part = music21.stream.Part()
        for chord_name in style_chords:
            if 'major' in chord_name:
                root = chord_name.split()[0]
                chord = music21.chord.Chord([root + '3', root + '4', root + '5'])
            elif 'minor' in chord_name:
                root = chord_name.split()[0]
                chord = music21.chord.Chord([root + '3', root + '4', root + '5'])
            elif '7' in chord_name:
                root = chord_name.replace('7', '')
                chord = music21.chord.Chord([root + '3', root + '4', root + '5', root + '6'])
            else:
                chord = music21.chord.Chord(['C3', 'E3', 'G3'])

            chord.quarterLength = 4.0  # Whole note
            harmony_part.append(chord)

        # Add parts to the main stream
        stream.append(melody_part)
        stream.append(harmony_part)

        # Add tempo marking
        tempo = music21.tempo.MetronomeMark(number=120)
        stream.insert(0, tempo)

        # Create temporary MIDI file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as temp_midi:
            stream.write('midi', temp_midi.name)
            midi_path = temp_midi.name

        return {"midi_file": midi_path, "composition": f"Generated {style} style composition using scale: {scale_name}"}

    except Exception as e:
        # Fallback: create a simple MIDI file if anything goes wrong
        stream = music21.stream.Stream()
        for note_name in ['C4', 'D4', 'E4', 'F4', 'G4']:
            note = music21.note.Note(note_name)
            stream.append(note)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as temp_midi:
            stream.write('midi', temp_midi.name)
            midi_path = temp_midi.name

        return {"midi_file": midi_path, "composition": f"Simple fallback composition due to error: {str(e)}"}

# Build the workflow
workflow = StateGraph(MusicState)

workflow.add_node("melody_generator", melody_generator)
workflow.add_node("harmony_creator", harmony_creator)
workflow.add_node("rhythm_analyzer", rhythm_analyzer)
workflow.add_node("style_adapter", style_adapter)
workflow.add_node("midi_converter", midi_converter)

workflow.set_entry_point("melody_generator")

workflow.add_edge("melody_generator", "harmony_creator")
workflow.add_edge("harmony_creator", "rhythm_analyzer")
workflow.add_edge("rhythm_analyzer", "style_adapter")
workflow.add_edge("style_adapter", "midi_converter")
workflow.add_edge("midi_converter", END)

app = workflow.compile()