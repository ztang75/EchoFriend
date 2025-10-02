"""
Enhanced microphone test script with better audio playback
Run this before using EchoFriend
"""

import pyaudio
import wave
import keyboard
import time
import os

def list_audio_devices():
    """List all available audio devices"""
    audio = pyaudio.PyAudio()
    print("\n" + "="*60)
    print("Available Audio Devices:")
    print("="*60)
    
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        print(f"\nDevice {i}: {info['name']}")
        print(f"  Max Input Channels: {info['maxInputChannels']}")
        print(f"  Max Output Channels: {info['maxOutputChannels']}")
        print(f"  Default Sample Rate: {info['defaultSampleRate']}")
    
    audio.terminate()
    print("\n" + "="*60)

def test_microphone():
    """Test microphone recording with multiple playback methods"""
    
    print("="*60)
    print("🎤 Microphone Test v2")
    print("="*60)
    print("\nThis will test your microphone setup.")
    print("Press and HOLD SPACE to start recording...")
    print("Release SPACE to stop.\n")
    
    # Initialize PyAudio
    audio = pyaudio.PyAudio()
    
    # Recording parameters
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    
    print("Waiting for SPACE key...")
    keyboard.wait('space')
    
    print("🔴 Recording... (Release SPACE to stop)")
    print("💡 Speak loudly and clearly into your microphone!")
    
    # Open stream
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    
    frames = []
    
    # Record while space is pressed
    while keyboard.is_pressed('space'):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
    
    print("⏹️  Recording stopped")
    
    # Close stream
    stream.stop_stream()
    stream.close()
    
    # Check if we recorded anything
    if len(frames) == 0:
        print("⚠️  No audio was recorded! Press and HOLD space longer.")
        audio.terminate()
        return
    
    duration = len(frames) * CHUNK / RATE
    print(f"📊 Recorded {duration:.2f} seconds of audio")
    
    # Save recording
    filename = "test_recording.wav"
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    
    file_size = os.path.getsize(filename)
    print(f"✅ Test recording saved to: {filename} ({file_size} bytes)")
    
    # Try multiple playback methods
    print("\n" + "="*60)
    print("Testing Playback Methods:")
    print("="*60)
    
    # Method 1: Using PyAudio
    print("\n1️⃣ Trying PyAudio playback...")
    try:
        playback_with_pyaudio(filename, audio)
    except Exception as e:
        print(f"   ❌ PyAudio playback failed: {e}")
    
    # Method 2: Using pygame
    print("\n2️⃣ Trying pygame playback...")
    try:
        playback_with_pygame(filename)
    except Exception as e:
        print(f"   ❌ Pygame playback failed: {e}")
    
    # Method 3: Using Windows built-in
    print("\n3️⃣ Trying Windows Media Player...")
    try:
        playback_with_windows(filename)
    except Exception as e:
        print(f"   ❌ Windows playback failed: {e}")
    
    audio.terminate()
    
    print("\n" + "="*60)
    print("💡 If none of the methods worked:")
    print(f"   - Open '{filename}' manually with Windows Media Player")
    print("   - Check your speaker/headphone volume")
    print("   - Check Windows sound settings")
    print("="*60)

def playback_with_pyaudio(filename, audio):
    """Play audio using PyAudio"""
    print("   🔊 Playing with PyAudio...")
    
    with wave.open(filename, 'rb') as wf:
        # Open stream
        stream = audio.open(
            format=audio.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True
        )
        
        # Read and play
        chunk_size = 1024
        data = wf.readframes(chunk_size)
        
        while data:
            stream.write(data)
            data = wf.readframes(chunk_size)
        
        stream.stop_stream()
        stream.close()
    
    print("   ✅ PyAudio playback complete!")

def playback_with_pygame(filename):
    """Play audio using pygame"""
    import pygame
    
    print("   🔊 Playing with pygame...")
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    
    # Wait for playback to finish
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    
    print("   ✅ Pygame playback complete!")

def playback_with_windows(filename):
    """Play audio using Windows built-in player"""
    import subprocess
    
    print("   🔊 Opening with Windows Media Player...")
    # This will open the file in default media player
    os.startfile(filename)
    print("   ✅ File opened in default player!")

def check_audio_levels():
    """Check if we're actually recording audio"""
    print("\n" + "="*60)
    print("🎤 Audio Level Monitor")
    print("="*60)
    print("This will show if your microphone is picking up sound.")
    print("Press and HOLD SPACE to start monitoring...")
    print("Release SPACE to stop.\n")
    
    audio = pyaudio.PyAudio()
    
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    
    keyboard.wait('space')
    
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    
    print("📊 Monitoring... (speak into your microphone)")
    print("   Volume bars will show if sound is detected:\n")
    
    import struct
    
    while keyboard.is_pressed('space'):
        data = stream.read(CHUNK, exception_on_overflow=False)
        
        # Convert bytes to integers
        values = struct.unpack(f'{CHUNK}h', data)
        
        # Calculate RMS (volume level)
        rms = (sum(v*v for v in values) / len(values)) ** 0.5
        
        # Convert to decibels
        if rms > 0:
            db = 20 * (rms / 32768)  # Normalize to 0-1 range
            bars = int(db * 50)  # Scale to 50 characters
            print(f"\rVolume: |{'█' * bars}{' ' * (50-bars)}| {db*100:.1f}%", end='')
        
        time.sleep(0.05)
    
    print("\n\n⏹️  Monitoring stopped")
    
    stream.stop_stream()
    stream.close()
    audio.terminate()

def main():
    """Main menu"""
    while True:
        print("\n" + "="*60)
        print("🎤 Microphone Testing Tool")
        print("="*60)
        print("\nChoose an option:")
        print("  1. List audio devices")
        print("  2. Test microphone (record & playback)")
        print("  3. Monitor audio levels")
        print("  4. Exit")
        print()
        
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == "1":
            list_audio_devices()
        elif choice == "2":
            test_microphone()
        elif choice == "3":
            check_audio_levels()
        elif choice == "4":
            print("\n👋 Goodbye!")
            break
        else:
            print("⚠️  Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main()