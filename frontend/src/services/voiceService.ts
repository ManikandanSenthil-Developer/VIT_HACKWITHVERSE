export interface VoiceRecognitionHandlers {
  onResult: (transcript: string) => void;
  onError: (error: string) => void;
  onEnd: () => void;
  lang?: 'en' | 'ta' | 'hi';
}

class BrowserVoiceService {
  private recognition: any = null;
  private isListening: boolean = false;

  constructor() {
    if (typeof window !== 'undefined') {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
      }
    }
  }

  public isVoiceInputSupported(): boolean {
    return !!this.recognition;
  }

  public isVoiceOutputSupported(): boolean {
    return typeof window !== 'undefined' && 'speechSynthesis' in window;
  }

  public startListening(handlers: VoiceRecognitionHandlers): void {
    if (!this.recognition) {
      handlers.onError('Voice input unavailable. You can type instead.');
      handlers.onEnd();
      return;
    }

    if (this.isListening) {
      this.stopListening();
    }

    const langCode =
      handlers.lang === 'ta' ? 'ta-IN' : handlers.lang === 'hi' ? 'hi-IN' : 'en-US';
    this.recognition.lang = langCode;

    this.recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      handlers.onResult(transcript);
    };

    this.recognition.onerror = (event: any) => {
      let msg = 'Voice input unavailable. You can type instead.';
      if (event.error === 'not-allowed') {
        msg = 'Microphone permission denied. You can type instead.';
      } else if (event.error === 'no-speech') {
        msg = 'No speech detected. Please try speaking again.';
      }
      handlers.onError(msg);
    };

    this.recognition.onend = () => {
      this.isListening = false;
      handlers.onEnd();
    };

    try {
      this.recognition.start();
      this.isListening = true;
    } catch (err) {
      handlers.onError('Voice input unavailable. You can type instead.');
      handlers.onEnd();
    }
  }

  public stopListening(): void {
    if (this.recognition && this.isListening) {
      try {
        this.recognition.stop();
      } catch (err) {
        // Ignore
      }
      this.isListening = false;
    }
  }

  public speak(text: string, lang?: 'en' | 'ta' | 'hi', onEnd?: () => void): void {
    if (!this.isVoiceOutputSupported()) return;

    window.speechSynthesis.cancel(); // Stop any pending utterances
    const cleanText = text.replace(/[•*#_`]/g, '').trim();
    const utterance = new SpeechSynthesisUtterance(cleanText);

    const langCode = lang === 'ta' ? 'ta-IN' : lang === 'hi' ? 'hi-IN' : 'en-US';
    utterance.lang = langCode;
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    if (onEnd) {
      utterance.onend = onEnd;
      utterance.onerror = onEnd;
    }

    window.speechSynthesis.speak(utterance);
  }

  public stopSpeaking(): void {
    if (this.isVoiceOutputSupported()) {
      window.speechSynthesis.cancel();
    }
  }

  public pauseSpeaking(): void {
    if (this.isVoiceOutputSupported()) {
      window.speechSynthesis.pause();
    }
  }

  public resumeSpeaking(): void {
    if (this.isVoiceOutputSupported()) {
      window.speechSynthesis.resume();
    }
  }
}

export const voiceService = new BrowserVoiceService();
