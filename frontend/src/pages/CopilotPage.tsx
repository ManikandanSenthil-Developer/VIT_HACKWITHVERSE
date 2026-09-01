import React, { useState, useEffect, useRef } from 'react';
import {
  Bot,
  Send,
  Sparkles,
  ShieldAlert,
  HelpCircle,
  Trash2,
  ChevronRight,
  TrendingUp,
  AlertTriangle,
  FileText,
  Activity,
  PlusCircle,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  ThumbsUp,
  ThumbsDown,
  ShieldCheck,
  Globe,
} from 'lucide-react';
import { copilotService } from '../services/copilotService';
import { useAccessibility } from '../context/AccessibilityContext';
import { voiceService } from '../services/voiceService';
import { ecosystemService } from '../services/ecosystemService';
import { DataProvenanceModal } from '../components/common/DataProvenanceModal';
import { CopilotConversationItem, CopilotChatResponse } from '../types';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  intent?: string;
  tool_calls?: string[];
  key_findings?: string[];
  evidence?: string[];
  risks?: string[];
  counterarguments?: string[];
  follow_ups?: string[];
  citations?: string[];
}

const QUICK_PROMPTS = [
  'Why did my portfolio risk increase?',
  'Compare NVDA and MSFT',
  'What happens if NVDA drops 10%?',
  'What changed since yesterday?',
  'Why is TSLA on my alert list?',
];

export const CopilotPage: React.FC = () => {
  const { preferences, setLanguage } = useAccessibility();
  const [conversations, setConversations] = useState<CopilotConversationItem[]>([]);
  const [activeConvId, setActiveConvId] = useState<number | undefined>(undefined);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputQuery, setInputQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Voice & Provenance State
  const [isListening, setIsListening] = useState(false);
  const [speakingMsgId, setSpeakingMsgId] = useState<string | null>(null);
  const [feedbackGiven, setFeedbackGiven] = useState<Record<string, boolean>>({});
  const [provenanceModalOpen, setProvenanceModalOpen] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const loadConversations = async () => {
    try {
      const convs = await copilotService.getConversations();
      setConversations(convs);
    } catch (err) {
      console.error('Failed to load conversations', err);
    }
  };

  const handleSelectConversation = async (convId: number) => {
    setActiveConvId(convId);
    try {
      const thread = await copilotService.getConversationThread(convId);
      const mapped: ChatMessage[] = thread.map((m) => ({
        id: String(m.id),
        role: m.role as 'user' | 'assistant',
        content: m.content,
        intent: m.intent,
        tool_calls: m.tool_calls,
        citations: m.citations,
      }));
      setMessages(mapped);
    } catch (err) {
      console.error('Failed to load conversation thread', err);
    }
  };

  const handleNewChat = () => {
    setActiveConvId(undefined);
    setMessages([]);
  };

  const handleDeleteConversation = async (e: React.MouseEvent, convId: number) => {
    e.stopPropagation();
    try {
      await copilotService.deleteConversation(convId);
      if (activeConvId === convId) {
        handleNewChat();
      }
      loadConversations();
    } catch (err) {
      console.error('Failed to delete conversation', err);
    }
  };

  const handleSend = async (queryText?: string) => {
    const textToSend = (queryText || inputQuery).trim();
    if (!textToSend || isLoading) return;

    const tempUserMsg: ChatMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: textToSend,
    };

    setMessages((prev) => [...prev, tempUserMsg]);
    setInputQuery('');
    setIsLoading(true);

    try {
      // Pass language preference
      const resp: CopilotChatResponse = await copilotService.chat(
        textToSend,
        activeConvId,
        preferences.language
      );
      if (!activeConvId) {
        setActiveConvId(resp.conversation_id);
        loadConversations();
      }

      const assistantMsg: ChatMessage = {
        id: String(resp.message_id),
        role: 'assistant',
        content: resp.summary,
        intent: resp.intent,
        tool_calls: resp.tool_calls,
        key_findings: resp.key_findings,
        evidence: resp.evidence,
        risks: resp.risks,
        counterarguments: resp.counterarguments,
        follow_ups: resp.follow_ups,
        citations: resp.citations,
      };

      setMessages((prev) => [...prev, assistantMsg]);

      // If voice enabled, speak summary automatically
      if (preferences.voice_enabled) {
        handleSpeakMessage(assistantMsg.id, resp.summary);
      }
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        role: 'assistant',
        content: `Error invoking Copilot: ${err?.response?.data?.detail || err.message || 'Execution failure.'}`,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleVoiceInput = () => {
    if (isListening) {
      voiceService.stopListening();
      setIsListening(false);
      return;
    }

    setIsListening(true);
    voiceService.startListening({
      lang: preferences.language,
      onResult: (transcript) => {
        setInputQuery(transcript);
        setIsListening(false);
      },
      onError: (err) => {
        setIsListening(false);
        console.warn('Voice input error:', err);
      },
      onEnd: () => {
        setIsListening(false);
      },
    });
  };

  const handleSpeakMessage = (id: string, text: string) => {
    if (speakingMsgId === id) {
      voiceService.stopSpeaking();
      setSpeakingMsgId(null);
      return;
    }
    setSpeakingMsgId(id);
    voiceService.speak(text, preferences.language, () => {
      setSpeakingMsgId(null);
    });
  };

  const handleFeedback = async (msgId: string, isHelpful: boolean) => {
    setFeedbackGiven((prev) => ({ ...prev, [msgId]: isHelpful }));
    try {
      await ecosystemService.submitFeedback({
        target_type: 'COPILOT_MESSAGE',
        target_id: msgId,
        is_helpful: isHelpful,
      });
    } catch (err) {
      console.error('Failed to submit feedback', err);
    }
  };

  return (
    <div className="flex h-[calc(100vh-5rem)] bg-slate-950 text-slate-100 rounded-xl overflow-hidden border border-slate-800 shadow-2xl">
      {/* Left Sidebar: Threads */}
      <div className="w-80 border-r border-slate-800 bg-slate-900/60 flex flex-col">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Bot className="w-5 h-5 text-indigo-400" />
            <h2 className="font-semibold text-sm tracking-wide">Research Threads</h2>
          </div>
          <button
            onClick={handleNewChat}
            className="p-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-300 transition-colors flex items-center space-x-1 text-xs"
            title="New Conversation"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>New</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {conversations.length === 0 ? (
            <div className="text-center py-8 text-slate-500 text-xs">No saved sessions yet.</div>
          ) : (
            conversations.map((conv) => (
              <div
                key={conv.id}
                onClick={() => handleSelectConversation(conv.id)}
                className={`group flex items-center justify-between p-2.5 rounded-lg cursor-pointer transition-colors text-xs ${
                  activeConvId === conv.id
                    ? 'bg-indigo-950/60 text-indigo-200 border border-indigo-800/40'
                    : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                }`}
              >
                <div className="flex items-center space-x-2 truncate">
                  <Bot className="w-3.5 h-3.5 flex-shrink-0" />
                  <span className="truncate">{conv.title}</span>
                </div>
                <button
                  onClick={(e) => handleDeleteConversation(e, conv.id)}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:text-rose-400 transition-opacity"
                  title="Delete thread"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))
          )}
        </div>

        <div className="p-3 border-t border-slate-800 bg-slate-950/40 text-[11px] text-slate-500 flex items-center space-x-1.5">
          <ShieldAlert className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
          <span>Decision Support Active • Non-Advisory</span>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-slate-950">
        {/* Top Header */}
        <div className="p-4 border-b border-slate-800 bg-slate-900/30 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-base text-white">MATS Financial Copilot</h1>
              <p className="text-xs text-slate-400">Autonomous Reasoning, SEC Citation & Multilingual Voice</p>
            </div>
          </div>

          {/* Language & Capabilities Badges */}
          <div className="flex items-center space-x-3 text-xs">
            {/* Language Switcher */}
            <div className="flex items-center space-x-1 bg-slate-900 border border-slate-800 rounded-lg p-1">
              <Globe className="w-3.5 h-3.5 text-indigo-400 ml-1.5" />
              {(['en', 'ta', 'hi'] as const).map((l) => (
                <button
                  key={l}
                  onClick={() => setLanguage(l)}
                  className={`px-2 py-0.5 rounded text-[11px] font-semibold transition-colors ${
                    preferences.language === l
                      ? 'bg-indigo-600 text-white'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {l === 'en' ? 'EN' : l === 'ta' ? 'தமிழ்' : 'हिन्दी'}
                </button>
              ))}
            </div>

            <span className="hidden sm:inline-flex items-center px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5 animate-pulse" />
              13 Safe Tools Online
            </span>
          </div>
        </div>

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center max-w-xl mx-auto space-y-6">
              <div className="w-16 h-16 rounded-2xl bg-indigo-950/60 border border-indigo-800/40 flex items-center justify-center shadow-xl">
                <Bot className="w-8 h-8 text-indigo-400" />
              </div>
              <div className="space-y-2">
                <h3 className="text-lg font-semibold text-slate-200">
                  {preferences.language === 'ta'
                    ? 'உங்கள் நிதி ஆராய்ச்சிக்கு எவ்வாறு உதவ முடியும்?'
                    : preferences.language === 'hi'
                    ? 'मैं आपके वित्तीय अनुसंधान में कैसे सहायता कर सकता हूँ?'
                    : 'How can I assist your financial research?'}
                </h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Synthesizes market data, official SEC Form 10-Ks, technical momentum, and deterministic risk
                  modeling. Speak or type your question in English, Tamil, or Hindi.
                </p>
              </div>

              {/* Quick Prompt Cards */}
              <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-2 text-left">
                {QUICK_PROMPTS.map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(prompt)}
                    className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-indigo-500/40 hover:bg-slate-900 transition-all text-xs text-slate-300 flex items-center justify-between group"
                  >
                    <span>{prompt}</span>
                    <ChevronRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-indigo-400 transition-colors" />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div
                key={index}
                className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
              >
                {msg.role === 'user' ? (
                  <div className="max-w-2xl bg-indigo-600 text-white px-4 py-3 rounded-2xl rounded-tr-sm text-sm shadow-md">
                    {msg.content}
                  </div>
                ) : (
                  <div className="max-w-3xl w-full bg-slate-900/80 border border-slate-800 rounded-2xl rounded-tl-sm p-5 space-y-4 shadow-xl">
                    {/* Tool Badges & Audio Controls */}
                    <div className="flex items-center justify-between flex-wrap gap-2">
                      {msg.tool_calls && msg.tool_calls.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 items-center">
                          <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500 mr-1">
                            Tools Invoked:
                          </span>
                          {msg.tool_calls.map((t, tidx) => (
                            <span
                              key={tidx}
                              className="inline-flex items-center px-2 py-0.5 rounded-md bg-indigo-950/70 border border-indigo-800/50 text-[10px] font-mono text-indigo-300"
                            >
                              ⚡ {t}
                            </span>
                          ))}
                        </div>
                      )}

                      {/* Voice Audio Speak & Provenance Buttons */}
                      <div className="flex items-center space-x-2 text-xs">
                        <button
                          onClick={() => handleSpeakMessage(msg.id, msg.content)}
                          className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center space-x-1"
                          title="Read aloud"
                        >
                          {speakingMsgId === msg.id ? (
                            <VolumeX className="w-3.5 h-3.5 text-indigo-400" />
                          ) : (
                            <Volume2 className="w-3.5 h-3.5" />
                          )}
                          <span className="text-[10px]">{speakingMsgId === msg.id ? 'Stop' : 'Listen'}</span>
                        </button>

                        <button
                          onClick={() => setProvenanceModalOpen(true)}
                          className="p-1.5 rounded-lg bg-indigo-950/40 hover:bg-indigo-900/60 border border-indigo-800/40 text-indigo-300 flex items-center space-x-1"
                          title="Show Data Provenance"
                        >
                          <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
                          <span className="text-[10px]">Show Source</span>
                        </button>
                      </div>
                    </div>

                    {/* Executive Summary */}
                    <div className="text-sm text-slate-200 leading-relaxed font-medium">
                      {msg.content}
                    </div>

                    {/* Key Findings */}
                    {msg.key_findings && msg.key_findings.length > 0 && (
                      <div className="space-y-1.5 bg-slate-950/50 p-3 rounded-xl border border-slate-800/60">
                        <div className="text-xs font-semibold text-slate-400 flex items-center space-x-1.5">
                          <TrendingUp className="w-3.5 h-3.5 text-indigo-400" />
                          <span>Key Analytical Findings</span>
                        </div>
                        <ul className="space-y-1 text-xs text-slate-300">
                          {msg.key_findings.map((k, kidx) => (
                            <li key={kidx} className="flex items-start space-x-2">
                              <span className="text-indigo-400 font-bold">•</span>
                              <span>{k}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Devil's Advocate / Counterarguments */}
                    {msg.counterarguments && msg.counterarguments.length > 0 && (
                      <div className="space-y-1.5 bg-amber-950/20 p-3 rounded-xl border border-amber-800/40">
                        <div className="text-xs font-semibold text-amber-300 flex items-center space-x-1.5">
                          <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                          <span>Devil's Advocate Challenges (Confirmation Bias Defense)</span>
                        </div>
                        <ul className="space-y-1 text-xs text-amber-200/90">
                          {msg.counterarguments.map((c, cidx) => (
                            <li key={cidx} className="flex items-start space-x-2">
                              <span className="text-amber-400 font-bold">⚠️</span>
                              <span>{c}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Grounding Citations & User Feedback */}
                    <div className="flex items-center justify-between pt-2 border-t border-slate-800/50 flex-wrap gap-2">
                      <div className="flex flex-wrap gap-1.5 items-center">
                        <span className="text-[10px] text-slate-500 flex items-center mr-1">
                          <FileText className="w-3 h-3 mr-1" />
                          Grounding Citations:
                        </span>
                        {(msg.citations && msg.citations.length > 0 ? msg.citations : ['SEC EDGAR 10-K']).map(
                          (c, cidx) => (
                            <span
                              key={cidx}
                              className="inline-flex items-center px-2 py-0.5 rounded bg-slate-800/60 text-slate-300 text-[10px]"
                            >
                              {c}
                            </span>
                          )
                        )}
                      </div>

                      {/* Helpful / Not Helpful Feedback Buttons */}
                      <div className="flex items-center space-x-1.5 text-xs text-slate-400">
                        <span className="text-[10px]">Helpful?</span>
                        <button
                          onClick={() => handleFeedback(msg.id, true)}
                          className={`p-1 rounded hover:text-white ${
                            feedbackGiven[msg.id] === true ? 'text-emerald-400' : ''
                          }`}
                          title="Vote Helpful"
                        >
                          <ThumbsUp className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleFeedback(msg.id, false)}
                          className={`p-1 rounded hover:text-white ${
                            feedbackGiven[msg.id] === false ? 'text-rose-400' : ''
                          }`}
                          title="Vote Not Helpful"
                        >
                          <ThumbsDown className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>

                    {/* Follow-up Prompts */}
                    {msg.follow_ups && msg.follow_ups.length > 0 && (
                      <div className="pt-2">
                        <div className="text-[11px] text-slate-400 mb-1.5 flex items-center space-x-1">
                          <HelpCircle className="w-3 h-3 text-indigo-400" />
                          <span>Suggested Next Questions:</span>
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {msg.follow_ups.map((f, fidx) => (
                            <button
                              key={fidx}
                              onClick={() => handleSend(f)}
                              className="px-2.5 py-1 rounded-lg bg-indigo-950/40 hover:bg-indigo-900/60 border border-indigo-800/40 text-indigo-200 text-xs transition-colors flex items-center space-x-1"
                            >
                              <span>{f}</span>
                              <ChevronRight className="w-3 h-3 text-indigo-400" />
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))
          )}

          {isLoading && (
            <div className="flex items-center space-x-3 text-slate-400 text-xs bg-slate-900/50 p-4 rounded-xl border border-slate-800 w-fit">
              <Activity className="w-4 h-4 text-indigo-400 animate-spin" />
              <span>Analyzing market telemetry, executing safe tools, and querying SEC RAG database...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/40">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center space-x-2"
          >
            <input
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              placeholder={
                isListening
                  ? 'Listening to speech...'
                  : preferences.language === 'ta'
                  ? 'கேள்வியைக் கேளுங்கள் (Ask in Tamil or English)...'
                  : preferences.language === 'hi'
                  ? 'प्रश्न पूछें (Ask in Hindi or English)...'
                  : "Ask a question (e.g. 'Why did my portfolio risk increase?' or 'Compare NVDA and MSFT')..."
              }
              className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
            />

            {/* Voice Input Microphone Button */}
            <button
              type="button"
              onClick={handleToggleVoiceInput}
              className={`p-3 rounded-xl border transition-all ${
                isListening
                  ? 'bg-rose-600 border-rose-500 text-white animate-pulse'
                  : 'bg-slate-900 border-slate-700 hover:border-indigo-500 text-slate-300'
              }`}
              title={isListening ? 'Stop voice listening' : 'Start voice input'}
            >
              {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>

            <button
              type="submit"
              disabled={isLoading || !inputQuery.trim()}
              className="px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium text-sm flex items-center space-x-1.5 transition-all shadow-lg shadow-indigo-600/20"
            >
              <span>Send</span>
              <Send className="w-4 h-4" />
            </button>
          </form>
          <p className="mt-2 text-center text-[11px] text-slate-500">
            MATS Copilot provides autonomous decision support and comparative research. Trade execution is strictly disabled.
          </p>
        </div>
      </div>

      {/* Data Provenance Inspector Modal */}
      <DataProvenanceModal
        isOpen={provenanceModalOpen}
        onClose={() => setProvenanceModalOpen(false)}
      />
    </div>
  );
};
export default CopilotPage;
