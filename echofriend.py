"""
EchoFriend - Interactive Language Learning Assistant
A conversational Dutch learning tool with real-time voice interaction
"""

import os
from openai import OpenAI
from pathlib import Path
import time
import pyaudio
import wave
import keyboard
import traceback

# Try to load from .env file if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Initialize OpenAI client with custom base_url if provided
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

if base_url:
    print(f"🔗 Using custom API endpoint: {base_url}")
    client = OpenAI(api_key=api_key, base_url=base_url)
else:
    client = OpenAI(api_key=api_key)

class AudioRecorder:
    """
    Handles real-time microphone recording
    Press and hold a key to record, release to stop
    """
    
    def __init__(self, sample_rate=44100, channels=1, chunk_size=1024, device_index=None):
        """
        Initialize audio recorder
        
        Parameters:
            sample_rate: Recording quality (44100 Hz is CD quality)
            channels: 1 for mono, 2 for stereo
            chunk_size: Number of frames per buffer
            device_index: Specific microphone device index (None = default)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.format = pyaudio.paInt16  # 16-bit audio
        self.device_index = device_index
        
        self.audio = pyaudio.PyAudio()
        
    def record_audio(self, filename):
        """
        Record audio from microphone using the same method as test_microphone.py
        
        Parameters:
            filename: Output file path
        Returns:
            Path to saved file or None if failed
        """
        frames = []
        
        try:
            print("\n🎤 Press and HOLD SPACE to record your voice...")
            print("   Release SPACE when you finish speaking")
            
            # Wait for user to press space
            keyboard.wait('space')
            
            print("🔴 Recording... (Release SPACE to stop)")
            print("💡 Speak clearly into your microphone!")
            
            # Open stream
            stream_params = {
                'format': self.format,
                'channels': self.channels,
                'rate': self.sample_rate,
                'input': True,
                'frames_per_buffer': self.chunk_size
            }
            
            if self.device_index is not None:
                stream_params['input_device_index'] = self.device_index
            
            stream = self.audio.open(**stream_params)
            
            # Record while space is pressed
            while keyboard.is_pressed('space'):
                try:
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                    frames.append(data)
                except Exception as e:
                    print(f"\n⚠️  Recording error: {e}")
                    break
            
            print("\n⏹️  Recording stopped")
            
            # Close stream
            stream.stop_stream()
            stream.close()
            
            # Check if we recorded anything
            if len(frames) == 0:
                print("⚠️  No audio was recorded! Press and HOLD space longer.")
                return None
            
            duration = len(frames) * self.chunk_size / self.sample_rate
            print(f"📊 Recorded {duration:.2f} seconds of audio")
            
            # Save recording
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(frames))
            
            file_size = os.path.getsize(filename)
            print(f"✅ Recording saved: {filename} ({file_size} bytes)")
            
            if file_size < 1000:
                print(f"⚠️  Warning: Recording is very small. Did you speak?")
            
            return filename
            
        except Exception as e:
            print(f"❌ Recording error: {e}")
            traceback.print_exc()
            return None
    
    def cleanup(self):
        """Clean up audio resources"""
        try:
            self.audio.terminate()
        except:
            pass


class EchoFriend:
    """
    Main EchoFriend class
    Manages conversation flow, understands user intent, and provides feedback
    """
    
    def __init__(self, scenario="Supermarket Shopping", microphone_device_index=None):
        """
        Initialize EchoFriend
        
        Parameters:
            scenario: Learning scenario (e.g., "Supermarket Shopping", "Restaurant")
            microphone_device_index: Specific microphone device to use (None = default)
        """
        self.scenario = scenario
        self.conversation_history = []
        self.user_inputs = []
        self.microphone_device_index = microphone_device_index
        
        # Create directories for audio files
        self.audio_dir = Path("audio_files")
        self.audio_dir.mkdir(exist_ok=True)
        
        self.recorder = AudioRecorder(device_index=microphone_device_index)
        
    def start_conversation(self):
        """Initialize conversation with scenario setup"""
        welcome_message = (
            f"Welcome to EchoFriend! Today we'll practice Dutch in the "
            f"'{self.scenario}' scenario. Feel free to start speaking!"
        )
        print(f"\n🎯 {welcome_message}\n")
        
        # Set up system prompt
        self.system_prompt = f"""You are a friendly Dutch language learning assistant in a '{self.scenario}' scenario.

Your role guidelines:
1. **Confirm Understanding**: After the user speaks, naturally paraphrase and confirm what you understood
2. **Keep Conversation Flowing**: Don't correct immediately; demonstrate correct usage through natural dialogue
3. **Scenario Simulation**: Play the role of a relevant character (e.g., shop clerk, waiter)
4. **Encourage Expression**: Create a safe, non-judgmental environment

Example dialogue flow:
- User: "Ik wil... eh... een appel" (may have imperfect grammar)
- You: "Oh, you want an apple, right? We have very fresh apples! Red apples are on the left, green apples on the right. Which kind would you like?"

Important: Don't correct errors now. Just continue the conversation naturally."""
        
        self.conversation_history.append({
            "role": "system",
            "content": self.system_prompt
        })
    
    def record_user_input(self, turn_number):
        """
        Record audio from microphone
        
        Parameters:
            turn_number: Current conversation turn
        Returns:
            Path to recorded audio file
        """
        filename = str(self.audio_dir / f"user_input_{turn_number}.wav")
        return self.recorder.record_audio(filename)
    
    def speech_to_text(self, audio_file_path):
        """
        Convert speech to text using OpenAI Whisper
        Compatible with both standard OpenAI API and third-party APIs
        
        Parameters:
            audio_file_path: Path to audio file
        Returns:
            Transcribed text
        """
        try:
            print("\n🎧 Transcribing your speech...")
            print("   (This may take a few seconds...)")
            
            with open(audio_file_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="nl"  # Dutch language code
                )
            
            print("✅ Transcription complete!")
            
            # Handle different API response formats
            # Some third-party APIs return a string directly
            # Standard OpenAI API returns an object with .text attribute
            if isinstance(transcript, str):
                return transcript
            elif hasattr(transcript, 'text'):
                return transcript.text
            elif isinstance(transcript, dict) and 'text' in transcript:
                return transcript['text']
            else:
                print(f"⚠️  Unexpected transcript format: {type(transcript)}")
                print(f"   Content: {transcript}")
                return str(transcript)
            
        except Exception as e:
            print(f"❌ Speech recognition error: {e}")
            print(f"   Error details: {str(e)}")
            traceback.print_exc()
            return None
    
    def generate_response(self, user_text):
        """
        Generate AI response using GPT-4
        
        Parameters:
            user_text: User's input text
        Returns:
            AI's response text
        """
        try:
            # Save user input for later analysis
            self.user_inputs.append({
                "text": user_text,
                "timestamp": len(self.conversation_history)
            })
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_text
            })
            
            print("\n🤔 AI is thinking...")
            print("   (Generating response...)")
            
            # Call GPT-4 to generate response
            response = client.chat.completions.create(
                model="gpt-4",
                messages=self.conversation_history,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Save AI response
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_response
            })
            
            print("✅ Response generated!")
            return ai_response
            
        except Exception as e:
            print(f"❌ AI response error: {e}")
            print(f"   Error details: {str(e)}")
            traceback.print_exc()
            return None
    
    def text_to_speech(self, text, turn_number):
        """
        Convert text to speech using OpenAI TTS
        
        Parameters:
            text: Text to convert
            turn_number: Current conversation turn
        Returns:
            Path to generated audio file
        """
        try:
            print("\n🔊 Generating AI voice response...")
            print("   (Converting text to speech...)")
            
            speech_file_path = self.audio_dir / f"ai_response_{turn_number}.mp3"
            
            response = client.audio.speech.create(
                model="tts-1",
                voice="nova",  # Female voice, good for learning
                input=text,
                speed=0.9  # Slightly slower for language learning
            )
            
            response.stream_to_file(speech_file_path)
            print("✅ Voice generated!")
            return speech_file_path
            
        except Exception as e:
            print(f"❌ Text-to-speech error: {e}")
            print(f"   Error details: {str(e)}")
            traceback.print_exc()
            return None
    
    def play_audio(self, audio_file_path):
        """
        Play audio file
        
        Parameters:
            audio_file_path: Path to audio file to play
        """
        try:
            print("\n🔊 Playing AI response...")
            
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(str(audio_file_path))
            pygame.mixer.music.play()
            
            # Wait for audio to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            print("✅ Playback complete!")
                
        except ImportError:
            print("⚠️  pygame not installed. Install with: pip install pygame")
            print(f"💡 Audio saved to: {audio_file_path}")
            print("   You can play it manually")
        except Exception as e:
            print(f"❌ Audio playback error: {e}")
            print(f"💡 Audio saved to: {audio_file_path}")
            traceback.print_exc()
    
    def process_conversation_turn(self, turn_number):
        """
        Process one complete conversation turn
        
        Flow:
        1. Record user's voice
        2. Speech → Text (Whisper)
        3. Generate AI response (GPT-4)
        4. Text → Speech (TTS)
        5. Play response
        
        Parameters:
            turn_number: Current turn number
        Returns:
            True if successful, False otherwise
        """
        print(f"\n{'='*60}")
        print(f"Starting Turn {turn_number}")
        print(f"{'='*60}")
        
        # Step 1: Record audio
        print("\n[Step 1/5] Recording your voice...")
        audio_file = self.record_user_input(turn_number)
        if not audio_file:
            print("❌ Step 1 failed: Could not record audio")
            return False
        
        # Step 2: Speech to text
        print("\n[Step 2/5] Converting speech to text...")
        user_text = self.speech_to_text(audio_file)
        if not user_text:
            print("❌ Step 2 failed: Could not transcribe audio")
            return False
        
        print(f"\n📝 You said: \"{user_text}\"")
        
        # Step 3: Generate response
        print("\n[Step 3/5] Generating AI response...")
        ai_response = self.generate_response(user_text)
        if not ai_response:
            print("❌ Step 3 failed: Could not generate response")
            return False
        
        print(f"\n💬 AI responds: \"{ai_response}\"")
        
        # Step 4: Text to speech
        print("\n[Step 4/5] Converting response to speech...")
        audio_response = self.text_to_speech(ai_response, turn_number)
        if not audio_response:
            print("❌ Step 4 failed: Could not generate audio")
            return False
        
        # Step 5: Play audio
        print("\n[Step 5/5] Playing response...")
        self.play_audio(audio_response)
        print(f"\n✅ Turn {turn_number} complete!")
        
        return True
    
    def generate_feedback(self):
        """
        Generate structured learning feedback after conversation
        Uses XAI (Explainable AI) principles for detailed analysis
        """
        print("\n" + "="*60)
        print("📊 Generating learning feedback...")
        print("="*60 + "\n")
        
        try:
            # Build feedback prompt
            feedback_prompt = f"""Please analyze the following Dutch language learning conversation and provide detailed structured feedback.

Conversation history:
{self._format_conversation_for_analysis()}

Please provide feedback in the following structure:

1. **Overall Performance Summary**
   - How effective was the communication?
   - Was the scenario task completed successfully?

2. **Language Highlights** (What went well)
   - Correctly used vocabulary or sentence patterns
   - Clear expressions

3. **Improvement Suggestions** (Gentle and constructive)
   - Grammar issues and correct usage
   - Vocabulary choice recommendations
   - Pronunciation tips (if can be inferred from text)

4. **Next Practice Focus**
   - Specific language points to practice
   - Suggested new scenarios to try

5. **Encouragement**
   - Positive feedback on learning progress

Please use a friendly, encouraging tone. The focus is on building learner confidence."""
            
            # Generate feedback using GPT-4
            feedback_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an experienced, gentle, and patient language teacher."
                    },
                    {"role": "user", "content": feedback_prompt}
                ],
                temperature=0.5
            )
            
            feedback = feedback_response.choices[0].message.content
            return feedback
            
        except Exception as e:
            print(f"❌ Error generating feedback: {e}")
            traceback.print_exc()
            return "Sorry, could not generate feedback due to an error."
    
    def _format_conversation_for_analysis(self):
        """Format conversation history for analysis"""
        formatted = []
        for msg in self.conversation_history:
            if msg["role"] == "user":
                formatted.append(f"Learner: {msg['content']}")
            elif msg["role"] == "assistant":
                formatted.append(f"Assistant: {msg['content']}")
        return "\n".join(formatted)
    
    def cleanup(self):
        """Clean up resources"""
        try:
            self.recorder.cleanup()
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")


def main():
    """Main function - Run EchoFriend"""
    
    print("="*60)
    print("🌟 EchoFriend - Interactive Language Learning Assistant")
    print("="*60)
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Error: OPENAI_API_KEY environment variable not set")
        print("\nPlease set it in .env file:")
        print("  OPENAI_API_KEY=your-api-key-here")
        print("  OPENAI_BASE_URL=your-api-base-url (if using third-party API)")
        return
    
    print("✅ API key found")
    
    # Show base URL if custom
    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        print(f"✅ Using custom API endpoint: {base_url}")
    else:
        print("✅ Using default OpenAI endpoint")
    
    # Optional: Ask for specific microphone device
    microphone_device = None
    use_specific = input("\nDo you want to select a specific microphone? (y/n): ").strip().lower()
    
    if use_specific == 'y':
        audio = pyaudio.PyAudio()
        print("\nAvailable microphones:")
        devices = []
        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                devices.append(i)
                print(f"  [{len(devices)}] {info['name']}")
        audio.terminate()
        
        if devices:
            try:
                choice = int(input(f"\nSelect microphone (1-{len(devices)}): "))
                if 1 <= choice <= len(devices):
                    microphone_device = devices[choice - 1]
                    print(f"✅ Using microphone device {microphone_device}")
            except:
                print("⚠️  Invalid choice, using default microphone")
    
    # Initialize EchoFriend
    echo_friend = EchoFriend(
        scenario="Supermarket Shopping",
        microphone_device_index=microphone_device
    )
    echo_friend.start_conversation()
    
    print("\n💡 Instructions:")
    print("   - Press and HOLD SPACE to record")
    print("   - Release SPACE to stop recording")
    print("   - Type 'quit' and press ENTER to end conversation\n")
    
    try:
        turn = 1
        while True:
            print(f"\n{'='*60}")
            print(f"Conversation Turn {turn}")
            print(f"{'='*60}")
            
            # Check if user wants to quit
            print("\nPress ENTER to start speaking, or type 'quit' to end: ", end='')
            user_choice = input().strip().lower()
            
            if user_choice in ['quit', 'exit', 'q']:
                print("\n👋 Ending conversation...")
                break
            
            # Process one conversation turn
            success = echo_friend.process_conversation_turn(turn)
            
            if not success:
                print("\n⚠️  Error processing turn.")
                retry = input("Do you want to try again? (y/n): ").strip().lower()
                if retry != 'y':
                    break
                continue
            
            turn += 1
        
        # Generate feedback if there was any conversation
        if len(echo_friend.user_inputs) > 0:
            feedback = echo_friend.generate_feedback()
            
            print("\n" + "="*60)
            print("📚 Learning Feedback")
            print("="*60)
            print(feedback)
            print("\n" + "="*60)
            print("Thank you for using EchoFriend! Keep practicing! 🎉")
            print("="*60)
        else:
            print("\nNo conversation recorded. See you next time!")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Program interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        traceback.print_exc()
    finally:
        # Clean up resources
        print("\n🧹 Cleaning up...")
        echo_friend.cleanup()
        print("✅ Cleanup complete!")


if __name__ == "__main__":
    main()