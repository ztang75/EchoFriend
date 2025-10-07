# EchoFriend - Interactive Dutch Language Learning Assistant (Ver1.0)

## 📖 Project Overview

EchoFriend is an innovative language learning tool that helps learners practice Dutch speaking skills through real-world scenario simulations. The system doesn't interrupt with corrections; instead, it confirms understanding through natural conversation and provides detailed feedback after the dialogue ends.

## 🎯 Core Features

- **Real-World Scenario Simulation**: Supermarket, restaurant, airport, and other daily scenarios
- **Smart Confirmation Mechanism**: AI paraphrases to confirm understanding
- **Delayed Feedback**: No interruptions during conversation; structured suggestions afterward
- **Voice Interaction**: Complete voice-based interaction with microphone input
- **Real-time Recording**: Press and hold SPACE to record, release to stop

## 🏗️ Technical Architecture

### Core Components

1. **Speech Recognition (Speech-to-Text)**
   - Service: OpenAI Whisper API
   - Function: Converts user voice to text
   - Language: Dutch (nl)

2. **Conversation Engine**
   - Service: OpenAI GPT-4
   - Function: Understands intent, generates natural responses, simulates scenario roles

3. **Speech Synthesis (Text-to-Speech)**
   - Service: OpenAI TTS API
   - Function: Converts AI responses to voice
   - Voice: Nova (female, clear for learning)
   - Speed: 0.9x (slightly slower for better comprehension)

4. **Audio Recording**
   - Library: PyAudio
   - Function: Real-time microphone recording
   - Control: Keyboard-based (SPACE key)

### Data Flow

```
┌─────────────────────┐
│ Press SPACE         │
│ Microphone Recording│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Save WAV file       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Whisper API         │
│ (Speech → Text)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ GPT-4               │
│ (Generate Response) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ TTS API             │
│ (Text → Speech)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Play AI Response    │
└─────────────────────┘
           │
           ▼ (Loop)
           
           ▼ (On Quit)
┌─────────────────────┐
│ GPT-4               │
│ (Generate Feedback) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Display Feedback    │
└─────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API Key
- Working microphone
- Speakers/headphones

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd echofriend
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set environment variable**

On Mac/Linux:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

On Windows (Command Prompt):
```cmd
set OPENAI_API_KEY=your-api-key-here
```

On Windows (PowerShell):
```powershell
$env:OPENAI_API_KEY="your-api-key-here"
```

4. **Run EchoFriend**
```bash
python echofriend.py
```

## 💡 Usage Example

### Example Conversation (Supermarket Scenario)

```
🎤 You: "Ik wil... eh... een appel"
🔊 AI: "Oh, you want an apple, right? We have very fresh apples! 
      Red apples are on the left, green apples on the right. 
      Which kind would you like?"

🎤 You: "Rode... hoeveel kost?"
🔊 AI: "I understand, you want to know the price of red apples. 
      Red apples are 2.5 euros per kilogram. How many would you like?"

🎤 You: "Twee stuks alstublieft"
🔊 AI: "Okay, two red apples. Let me pick two nice ones for you. 
      Do you need anything else?"

🎤 You: "Nee, dank u wel"
🔊 AI: "You're welcome! Two red apples, that's 1.2 euros total. 
      Have a great day!"
```

### Feedback Example

```
📚 Learning Feedback
============================================================

1. Overall Performance Summary
   ✅ Great communication! Despite some hesitation, you successfully 
   completed the apple purchase task.

2. Language Highlights
   ✨ "dank u wel" - Polite expression used correctly
   ✨ "twee stuks" - Number expression was clear
   ✨ "alstublieft" - Excellent use of courtesy word

3. Improvement Suggestions
   📝 "hoeveel kost?" → "Hoeveel kost het?" (add "het")
   💡 Practice question formation: "Wat kost dat?"
   🗣️ Try to form complete sentences to reduce pauses

4. Next Practice Focus
   🎯 Practice forming complete questions
   🎯 Learn more supermarket vocabulary (vegetables, fruits)
   🎯 Try the restaurant scenario to practice ordering

5. Encouragement
   🌟 Excellent work! You completed a full shopping dialogue. 
   Your confidence is growing - keep it up!
```

## 📁 Project Structure

```
echofriend/
│
├── echofriend.py           # Main program
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
│
├── audio_files/           # Automatically created
│   ├── user_input_1.wav
│   ├── ai_response_1.mp3
│   └── ...
│
└── .env                   # Environment variables (create this)
```

## 🔧 Technical Details (For Beginners)

### What is an API?

An API (Application Programming Interface) is like a "service window". You don't need to know how it works internally:
1. Send a request (e.g., send an audio file)
2. Receive a response (e.g., get transcribed text)

### Three Key OpenAI Services

1. **Whisper (Speech Recognition)**
   - Input: Audio file (WAV, MP3, etc.)
   - Output: Text
   - Example: `audio.wav` → `"Ik wil een appel"`

2. **GPT-4 (Text Understanding and Generation)**
   - Input: Conversation history + new message
   - Output: AI response
   - Example: `"Ik wil een appel"` → `"Oh, you want an apple..."`

3. **TTS (Text-to-Speech)**
   - Input: Text
   - Output: Audio file
   - Example: `"Oh, you want..."` → `response.mp3`

### Why You Don't Need ML Background

We use **pre-trained models**, which means:
- ✅ No need to prepare training data
- ✅ No need to train models
- ✅ No need to understand neural networks
- ✅ Just call the API

It's as simple as using a mobile app!

### How Microphone Recording Works

```python
# 1. Initialize audio recorder
recorder = AudioRecorder()

# 2. When user presses SPACE
recorder.start_recording()  # Start capturing audio

# 3. When user releases SPACE
recorder.stop_recording()   # Stop capturing

# 4. Save to file
recorder.save_recording("output.wav")
```

The `pyaudio` library handles all the complex audio processing!

## 🎨 Customization Ideas

### Change Scenarios

Edit the scenario in `echofriend.py`:

```python
# Instead of supermarket:
echo_friend = EchoFriend(scenario="Restaurant Dining")
# or
echo_friend = EchoFriend(scenario="At the Doctor's Office")
# or
echo_friend = EchoFriend(scenario="Job Interview")
```

### Change Voice Settings

Modify in the `text_to_speech` method:

```python
response = client.audio.speech.create(
    model="tts-1-hd",     # Higher quality
    voice="alloy",        # Different voice: alloy, echo, fable, onyx, nova, shimmer
    input=text,
    speed=1.0             # Normal speed (0.25 to 4.0)
)
```

## 🐛 Troubleshooting

### "No module named 'pyaudio'"

On Mac:
```bash
brew install portaudio
pip install pyaudio
```

On Ubuntu/Debian:
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

On Windows:
```bash
pip install pipwin
pipwin install pyaudio
```

### "No module named 'pygame'"

```bash
pip install pygame
```

### Microphone not working

- Check system permissions for microphone access
- Test microphone with other applications first
- Try running Python with administrator/sudo privileges

### API Key Error

Make sure your OpenAI API key is set:
```bash
echo $OPENAI_API_KEY  # Should display your key
```

## 📝 License

MIT License

## 🤝 Contributing

Issues and Pull Requests are welcome!

---

**Happy Learning! 🎉**

