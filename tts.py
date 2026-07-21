import os
import sys
import platform
import asyncio
import edge_tts

# Reconfigure stdout/stderr to use UTF-8 encoding to prevent UnicodeEncodeError on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


def format_tamil_text(text):
    """
    Formats classical Tamil text (especially Thirukkural) to introduce natural pauses.
    - If it's a 2-line input, joins them with a comma for a natural breath pause.
    - If it's a single line with exactly 7 words (standard Thirukkural structure),
      automatically splits it into 4 words and 3 words with a comma in between.
    """
    # Clean and check line structure
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if len(lines) == 2:
        formatted = f"{lines[0]}, {lines[1]}."
        print(f"📝 Two-line structure detected. Auto-formatted for native breath pause:\n   \"{formatted}\"\n")
        return formatted
        
    # Check word count for standard single-line Thirukkural (exactly 7 words)
    cleaned_text = " ".join(text.strip().split())
    words = cleaned_text.split()
    if len(words) == 7:
        line1 = " ".join(words[:4])
        line2 = " ".join(words[4:])
        formatted = f"{line1}, {line2}."
        print(f"📝 Thirukkural detected (7 words). Auto-formatted for native breath pause:\n   \"{formatted}\"\n")
        return formatted
        
    return text


async def text_to_speech(text, voice='ta-IN-PallaviNeural', rate='-12%', output_filename='speech_output.mp3'):
    """
    Converts text to speech using Microsoft Edge Neural TTS API via edge-tts
    and saves it to an MP3 file.
    """
    # Auto-format for natural pauses
    formatted_text = format_tamil_text(text)
    
    print(f"Generating speech...")
    print(f"   Voice: {voice}")
    print(f"   Speed Rate: {rate} (Slower speeds improve classical pronunciation)")
    
    try:
        communicate = edge_tts.Communicate(formatted_text, voice, rate=rate)
        await communicate.save(output_filename)
        print(f"✅ Success! Audio saved to: {output_filename}")
        return output_filename
    except Exception as e:
        print(f"❌ Failed to generate speech. Error: {e}")
        return None


def play_audio(filename):
    """
    Plays the generated audio file using the default system media player.
    """
    if not os.path.exists(filename):
        print("❌ Audio file does not exist.")
        return
        
    print(f"🔊 Playing audio file: {filename}...")
    try:
        system_name = platform.system()
        if system_name == "Windows":
            os.startfile(filename)
        elif system_name == "Darwin":  # macOS
            os.system(f"open '{filename}'")
        else:  # Linux
            os.system(f"xdg-open '{filename}'")
    except Exception as e:
        print(f"⚠️ Could not automatically play the file: {e}")
        print(f"Please play the file manually from: {os.path.abspath(filename)}")


async def amain():
    print("==================================================")
    print("        OPTIMIZED TAMIL TEXT TO SPEECH (TTS)      ")
    print("==================================================")
    
    # 1. Select Voice
    print("Choose Voice:")
    print("1. Pallavi (Female - Default)")
    print("2. Valluvar (Male)")
    voice_choice = input("Enter choice (1 or 2, default is 1): ").strip()
    
    voice = "ta-IN-PallaviNeural"
    if voice_choice == "2":
        voice = "ta-IN-ValluvarNeural"
        
    # 2. Select Speed Rate
    print("\nChoose Speed Rate:")
    print("1. Poetic / Slow (-12%) [Recommended for natural tone]")
    print("2. Very Slow (-20%) [For precise syllable pronunciation]")
    print("3. Normal (+0%)")
    rate_choice = input("Enter choice (1, 2, or 3, default is 1): ").strip()
    
    rate = "-12%"
    if rate_choice == "2":
        rate = "-20%"
    elif rate_choice == "3":
        rate = "+0%"
        
    # Default text: Thirukkural couplet
    default_text = "துப்பார்க்குத் துப்பாய துப்பாக்கித் துப்பார்க்குத் துப்பாய தூஉம் மழை"
    
    print(f"\nEnter the text to speak (Press Enter for default: '{default_text}'):")
    text = input().strip()
    
    if not text:
        text = default_text
        
    output_file = "speech_output.mp3"
    
    # Generate TTS
    file_created = await text_to_speech(text, voice=voice, rate=rate, output_filename=output_file)
    
    # Play TTS
    if file_created:
        play_audio(file_created)


def main():
    asyncio.run(amain())


if __name__ == "__main__":
    main()
