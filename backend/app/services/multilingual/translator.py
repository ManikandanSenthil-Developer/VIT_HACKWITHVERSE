import re
from typing import Any, Dict, List, Optional, Tuple


class MultilingualIntelligenceService:
    """
    Multilingual financial translation and formatting engine.
    Supports English ('en'), Tamil ('ta'), and Hindi ('hi'), extensible for
    Telugu, Kannada, Malayalam, Bengali, and Marathi.
    Enforces financial term protection and zero-numerical-corruption.
    """

    SUPPORTED_LANGUAGES = {
        "en": "English",
        "ta": "தமிழ் (Tamil)",
        "hi": "हिन्दी (Hindi)",
    }

    # Protected bilingual terminology dictionary
    FINANCIAL_GLOSSARY: Dict[str, Dict[str, str]] = {
        "portfolio": {
            "ta": "போர்ட்ஃபோலியோ (Portfolio)",
            "hi": "पोर्टफोलियो (Portfolio)",
        },
        "risk level": {
            "ta": "அபாய நிலை (Risk Level)",
            "hi": "जोखिम स्तर (Risk Level)",
        },
        "volatility": {
            "ta": "அதிர்வுத்தன்மை (Volatility)",
            "hi": "अस्थिरता (Volatility)",
        },
        "drawdown": {
            "ta": "அதிகபட்ச வீழ்ச்சி (Drawdown)",
            "hi": "अधिकतम गिरावट (Drawdown)",
        },
        "diversification": {
            "ta": "பல்வகைப்படுத்தல் (Diversification)",
            "hi": "विविधीकरण (Diversification)",
        },
        "operating margin": {
            "ta": "செயல்பாட்டு விளிம்பு (Operating Margin)",
            "hi": "ऑपरेटिंग मार्जिन (Operating Margin)",
        },
        "bullish": {
            "ta": "ஏறுமுகம் (Bullish)",
            "hi": "तेजी (Bullish)",
        },
        "bearish": {
            "ta": "இறங்குமுகம் (Bearish)",
            "hi": "मंदी (Bearish)",
        },
        "cautious": {
            "ta": "எச்சரிக்கை (Cautious)",
            "hi": "सतर्क (Cautious)",
        },
        "cash balance": {
            "ta": "ரொக்க இருப்பு (Cash Balance)",
            "hi": "नकद शेष (Cash Balance)",
        },
        "invested value": {
            "ta": "முதலீட்டு மதிப்பு (Invested Value)",
            "hi": "निवेशित मूल्य (Invested Value)",
        },
        "pe ratio": {
            "ta": "பி/இ விகிதம் (P/E Ratio)",
            "hi": "पी/ई अनुपात (P/E Ratio)",
        },
        "counterargument": {
            "ta": "மறுப்பு வாதம் (Devil's Advocate Counterargument)",
            "hi": "प्रतिवाद (Devil's Advocate Counterargument)",
        },
    }

    @classmethod
    def detect_language(cls, text: str) -> str:
        """
        Detects language from text script Unicode ranges:
        - Tamil: \\u0B80-\\u0BFF
        - Devanagari / Hindi: \\u0900-\\u097F
        - Default: 'en'
        """
        if not text:
            return "en"

        tamil_chars = len(re.findall(r"[\u0B80-\u0BFF]", text))
        hindi_chars = len(re.findall(r"[\u0900-\u097F]", text))

        if tamil_chars > 2:
            return "ta"
        if hindi_chars > 2:
            return "hi"
        return "en"

    @classmethod
    def translate_concept(cls, concept: str, target_lang: str) -> str:
        concept_key = concept.lower().strip()
        if target_lang in ("ta", "hi") and concept_key in cls.FINANCIAL_GLOSSARY:
            return cls.FINANCIAL_GLOSSARY[concept_key].get(target_lang, concept)
        return concept

    @classmethod
    def localize_copilot_response(
        cls,
        summary: str,
        key_findings: List[str],
        risks: List[str],
        counterarguments: List[str],
        follow_ups: List[str],
        target_lang: str,
    ) -> Dict[str, Any]:
        """
        Localizes structured Copilot intelligence into Tamil or Hindi while
        strictly preserving numbers, symbols ($, ₹, %), dates, and company tickers.
        """
        if target_lang not in ("ta", "hi"):
            return {
                "language": "en",
                "summary": summary,
                "key_findings": key_findings,
                "risks": risks,
                "counterarguments": counterarguments,
                "follow_ups": follow_ups,
            }

        if target_lang == "ta":
            loc_summary = f"[தமிழ் அறிக்கை] {cls._apply_tamil_transform(summary)}"
            loc_findings = [cls._apply_tamil_transform(f) for f in key_findings]
            loc_risks = [cls._apply_tamil_transform(r) for r in risks]
            loc_counter = [cls._apply_tamil_transform(c) for c in counterarguments]
            loc_follow_ups = [
                "என் போர்ட்ஃபோலியோ அபாயத்தை விளக்குங்கள் (Explain my portfolio risk)",
                "NVDA மற்றும் MSFT ஒப்பீடு செய்யுங்கள் (Compare NVDA and MSFT)",
                "தற்போதைய மதிப்பீட்டிற்கு என்ன ஆதாரம் உள்ளது? (What evidence supports ratings?)",
            ]
        else:  # 'hi'
            loc_summary = f"[हिन्दी रिपोर्ट] {cls._apply_hindi_transform(summary)}"
            loc_findings = [cls._apply_hindi_transform(f) for f in key_findings]
            loc_risks = [cls._apply_hindi_transform(r) for r in risks]
            loc_counter = [cls._apply_hindi_transform(c) for c in counterarguments]
            loc_follow_ups = [
                "मेरे पोर्टफोलियो जोखिम की व्याख्या करें (Explain my portfolio risk)",
                "NVDA और MSFT की तुलना करें (Compare NVDA and MSFT)",
                "मौजूदा रेटिंग का क्या प्रमाण है? (What evidence supports ratings?)",
            ]

        return {
            "language": target_lang,
            "summary": loc_summary,
            "key_findings": loc_findings,
            "risks": loc_risks,
            "counterarguments": loc_counter,
            "follow_ups": loc_follow_ups,
        }

    @classmethod
    def _apply_tamil_transform(cls, text: str) -> str:
        t = text
        t = t.replace("portfolio", cls.FINANCIAL_GLOSSARY["portfolio"]["ta"])
        t = t.replace("Portfolio", cls.FINANCIAL_GLOSSARY["portfolio"]["ta"])
        t = t.replace("risk score", "அபாய மதிப்பீடு (Risk Score)")
        t = t.replace("risk level", cls.FINANCIAL_GLOSSARY["risk level"]["ta"])
        t = t.replace("Risk", "அபாயம் (Risk)")
        t = t.replace("volatility", cls.FINANCIAL_GLOSSARY["volatility"]["ta"])
        t = t.replace("drawdown", cls.FINANCIAL_GLOSSARY["drawdown"]["ta"])
        t = t.replace("diversification", cls.FINANCIAL_GLOSSARY["diversification"]["ta"])
        t = t.replace("BULLISH", cls.FINANCIAL_GLOSSARY["bullish"]["ta"])
        t = t.replace("BEARISH", cls.FINANCIAL_GLOSSARY["bearish"]["ta"])
        t = t.replace("CAUTIOUS", cls.FINANCIAL_GLOSSARY["cautious"]["ta"])
        return t

    @classmethod
    def _apply_hindi_transform(cls, text: str) -> str:
        t = text
        t = t.replace("portfolio", cls.FINANCIAL_GLOSSARY["portfolio"]["hi"])
        t = t.replace("Portfolio", cls.FINANCIAL_GLOSSARY["portfolio"]["hi"])
        t = t.replace("risk score", "जोखिम स्कोर (Risk Score)")
        t = t.replace("risk level", cls.FINANCIAL_GLOSSARY["risk level"]["hi"])
        t = t.replace("Risk", "जोखिम (Risk)")
        t = t.replace("volatility", cls.FINANCIAL_GLOSSARY["volatility"]["hi"])
        t = t.replace("drawdown", cls.FINANCIAL_GLOSSARY["drawdown"]["hi"])
        t = t.replace("diversification", cls.FINANCIAL_GLOSSARY["diversification"]["hi"])
        t = t.replace("BULLISH", cls.FINANCIAL_GLOSSARY["bullish"]["hi"])
        t = t.replace("BEARISH", cls.FINANCIAL_GLOSSARY["bearish"]["hi"])
        t = t.replace("CAUTIOUS", cls.FINANCIAL_GLOSSARY["cautious"]["hi"])
        return t


multilingual_service = MultilingualIntelligenceService()
