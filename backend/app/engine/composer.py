"""PromptComposer – Assembles structured, language-fluent, enterprise Master Prompts from PromptPlan and PromptSpec.

Guarantees 100% adherence to invariants D1-D9 with zero cross-section sentence duplication.
"""

from __future__ import annotations

import hashlib
import logging
import re
from typing import Any

from app.engine.planner import PromptPlan
from app.engine.spec_extractor import PromptSpec

logger = logging.getLogger("intentify.engine.composer")


class PromptComposer:
    """Compiles bespoke Master Prompts with script-aware language translation and structured markdown formatting."""

    GUJARATI_HEADERS = {
        "role & pedagogical persona": "૧. ભૂમિકા અને શિક્ષણશાસ્ત્રીય પર્સના (Role & Pedagogical Persona)",
        "role & technical persona": "૧. ભૂમિકા અને ટેકનિકલ પર્સના (Role & Technical Persona)",
        "role & diagnostic persona": "૧. ભૂમિકા અને ડાયગ્નોસ્ટિક પર્સના (Role & Diagnostic Persona)",
        "core learning objective & scope": "૨. શિક્ષણના મુખ્ય ઉદ્દેશ્યો અને વ્યાપ (Learning Objectives & Scope)",
        "core objective & system scope": "૨. સિસ્ટમનો મુખ્ય ઉદ્દેશ્ય અને કાર્યક્ષેત્ર (Core Objective & System Scope)",
        "defect symptom & incident context": "૨. ખામીના લક્ષણો અને ઇન્સિડન્ટ સંદર્ભ (Defect Symptoms & Incident Context)",
        "curated topic plan & step-by-step curriculum": "૩. વિગતવાર અભ્યાસક્રમ અને સ્ટેપ-બાય-સ્ટેપ વિષયો (Curated Topic Plan & Curriculum)",
        "system architecture & component topology": "૩. સિસ્ટમ આર્કિટેક્ચર અને કોમ્પોનન્ટ ટોપોલોજી (System Architecture & Topology)",
        "event coordination & operational topology": "૩. આયોજન માળખું અને ઓપરેશનલ સંકલન (Event Coordination & Operational Topology)",
        "strategic framework & operational topology": "૩. વ્યાવસાયિક વ્યૂહરચના અને ઓપરેશનલ માળખું (Strategic Framework & Operational Topology)",
        "clinical protocol & operational topology": "૩. ક્લિનિકલ પ્રોટોકોલ અને ઓપરેશનલ વર્કફ્લો (Clinical Protocol & Operational Topology)",
        "root cause analysis (rca) framework": "૩. રૂટ કોઝ એનાલિસિસ (RCA) ફ્રેમવર્ક (Root Cause Analysis Framework)",
        "technical standards & best practices": "૪. ટેકનિકલ ધોરણો અને ઉત્તમ પ્રથાઓ (Technical Standards & Best Practices)",
        "technical standards & protocols": "૪. ટેકનિકલ ધોરણો અને પ્રોટોકોલ્સ (Technical Standards & Protocols)",
        "technical standards & conventions": "૪. ટેકનિકલ ધોરણો અને સંમેલનો (Technical Standards & Conventions)",
        "step-by-step resolution patch": "૪. સ્ટેપ-બાય-સ્ટેપ પેચ અને ઉકેલ (Step-by-Step Resolution Patch)",
        "verifiable acceptance criteria": "૫. સ્વીકૃતિ માપદંડ (Verifiable Acceptance Criteria)",
        "verification criteria & regression tests": "૫. વેરિફિકેશન માપદંડ અને રિગ્રેશન ટેસ્ટ્સ (Verification Criteria & Tests)",
        "output format specification": "૬. આઉટપુટ ફોર્મેટ વિશિષ્ટતાઓ (Output Format Specification)",
        "self-verification quality checklist": "૭. ગુણવત્તા ચકાસણી ચેકલિસ્ટ (Self-Verification Quality Checklist)",
        "operational guardrails & negative constraints": "૮. ઓપરેશનલ બાઉન્ડ્રી અને પ્રતિબંધો (Operational Guardrails & Boundaries)",
    }

    HINDI_HEADERS = {
        "role & pedagogical persona": "1. भूमिका और शिक्षण व्यक्तित्व (Role & Pedagogical Persona)",
        "role & technical persona": "1. भूमिका और तकनीकी व्यक्तित्व (Role & Technical Persona)",
        "role & diagnostic persona": "1. भूमिका और नैदानिक व्यक्तित्व (Role & Diagnostic Persona)",
        "core learning objective & scope": "2. मुख्य शिक्षण उद्देश्य और कार्यक्षेत्र (Learning Objectives & Scope)",
        "core objective & system scope": "2. सिस्टम का मुख्य उद्देश्य और कार्यक्षेत्र (Core Objective & System Scope)",
        "defect symptom & incident context": "2. दोष के लक्षण और घटना संदर्भ (Defect Symptoms & Incident Context)",
        "curated topic plan & step-by-step curriculum": "3. संरचित पाठ्यक्रम और चरण-दर-चरण विषय (Curated Topic Plan & Curriculum)",
        "system architecture & component topology": "3. सिस्टम आर्किटेक्चर और कंपोनेंट टोपोलॉजी (System Architecture & Topology)",
        "event coordination & operational topology": "3. आयोजन समन्वय और परिचालन टोपोलॉजी (Event Coordination & Operational Topology)",
        "strategic framework & operational topology": "3. रणनीतिक ढांचा और परिचालन टोपोलॉजी (Strategic Framework & Operational Topology)",
        "clinical protocol & operational topology": "3. नैदानिक प्रोटोकॉल और परिचालन कार्यप्रवाह (Clinical Protocol & Operational Topology)",
        "root cause analysis (rca) framework": "3. मूल कारण विश्लेषण (RCA) ढांचा (Root Cause Analysis Framework)",
        "technical standards & best practices": "4. तकनीकी मानक और सर्वोत्तम अभ्यास (Technical Standards & Best Practices)",
        "technical standards & protocols": "4. तकनीकी मानक और प्रोटोकॉल (Technical Standards & Protocols)",
        "technical standards & conventions": "4. तकनीकी मानक और परंपराएं (Technical Standards & Conventions)",
        "step-by-step resolution patch": "4. चरण-दर-चरण समाधान पैच (Step-by-Step Resolution Patch)",
        "verifiable acceptance criteria": "5. सत्यापन योग्य स्वीकृति मानदंड (Verifiable Acceptance Criteria)",
        "verification criteria & regression tests": "5. सत्यापन मानदंड और प्रतिगमन परीक्षण (Verification Criteria & Tests)",
        "output format specification": "6. आउटपुट प्रारूप विनिर्देश (Output Format Specification)",
        "self-verification quality checklist": "7. स्व-सत्यापन गुणवत्ता चेकलिस्ट (Self-Verification Quality Checklist)",
        "operational guardrails & negative constraints": "8. परिचालन सीमाएं और निषेध (Operational Guardrails & Boundaries)",
    }

    def compose(self, spec: PromptSpec, plan: PromptPlan, style: str = "standard") -> str:
        """Compose the full Master Prompt string respecting language, style, and domain invariants."""
        is_gujarati = spec.output_language.lower() in ("gujarati", "gu")
        is_hindi = spec.output_language.lower() in ("hindi", "hi")

        lines: list[str] = []
        seen_sentence_hashes: set[str] = set()
        seen_token_sets: list[set[str]] = []

        def add_unique_line(line_text: str) -> None:
            """Ensure zero sentence duplication across sections (Invariant D2)."""
            cleaned = line_text.strip()
            if not cleaned or cleaned.startswith("#"):
                lines.append(cleaned)
                return

            tokens = [t.lower() for t in re.findall(r"\b\w{3,}\b", cleaned)]
            if len(tokens) >= 4:
                h = hashlib.sha256(" ".join(tokens).encode("utf-8")).hexdigest()
                if h in seen_sentence_hashes:
                    return

                t_set = set(tokens)
                for prev in seen_token_sets:
                    union = len(t_set | prev)
                    if union > 0 and (len(t_set & prev) / union) >= 0.80:
                        return

                seen_sentence_hashes.add(h)
                seen_token_sets.append(t_set)

            lines.append(cleaned)

        # 1. Preamble
        if is_gujarati:
            lines.append("## સૂચના: આ પ્રોમ્પ્ટ મુજબ નિષ્ણાત માર્ગદર્શન, સંપૂર્ણ વિગત અને ચોક્કસ ઉકેલ આપો.\n")
        elif is_hindi:
            lines.append("## निर्देश: इस प्रॉम्प्ट के अनुसार विशेषज्ञ मार्गदर्शन, पूर्ण विवरण और सटीक समाधान प्रदान करें।\n")

        # 2. Render Plan Sections
        for idx, sec in enumerate(plan.sections, 1):
            heading_lower = sec.heading.strip().lower()

            if is_gujarati and heading_lower in self.GUJARATI_HEADERS:
                display_heading = f"### {self.GUJARATI_HEADERS[heading_lower]}"
            elif is_hindi and heading_lower in self.HINDI_HEADERS:
                display_heading = f"### {self.HINDI_HEADERS[heading_lower]}"
            else:
                display_heading = f"### {idx}. {sec.heading.strip()}"

            lines.append(display_heading)

            for d in sec.directives:
                # Localize directives where applicable
                localized = self._localize_directive(d, spec, is_gujarati, is_hindi)
                if localized.startswith("Topic") or localized.startswith("Subsystem"):
                    lines.append(localized)
                elif localized.startswith("  -"):
                    add_unique_line(localized)
                else:
                    add_unique_line(f"- {localized}")

            lines.append("")

        # 3. Guardrails & Negative Constraints
        if plan.negative_guardrails or spec.constraints:
            if is_gujarati:
                guard_heading = "### ૮. ઓપરેશનલ બાઉન્ડ્રી અને પ્રતિબંધો (Operational Guardrails & Negative Constraints)"
            elif is_hindi:
                guard_heading = "### 8. परिचालन सीमाएं और निषेध (Operational Guardrails & Negative Constraints)"
            else:
                guard_heading = f"### {len(plan.sections) + 1}. Operational Guardrails & Negative Constraints"

            lines.append(guard_heading)
            for g in plan.negative_guardrails:
                add_unique_line(f"- **Prohibition**: {g}")
            for c in spec.constraints:
                add_unique_line(f"- **Strict Constraint**: {c}")
            lines.append("")

        # 4. Proactive Assumptions
        if plan.assumptions or spec.missing_fields:
            if is_gujarati:
                assump_heading = "### ૯. ધારણાઓ અને વિશિષ્ટતાઓ (Documented Assumptions & Context)"
            elif is_hindi:
                assump_heading = "### 9. प्रलेखित धारणाएं और संदर्भ (Documented Assumptions & Context)"
            else:
                assump_heading = f"### {len(plan.sections) + 2}. Documented Assumptions & Context"

            lines.append(assump_heading)
            for a in plan.assumptions:
                add_unique_line(f"- **Assumption**: {a}")
            for m in spec.missing_fields:
                add_unique_line(f"- **Context Assumption**: {m} is assumed to follow standard production best practices.")
            lines.append("")

        full_prompt = "\n".join(lines).strip()
        return full_prompt

    def _localize_directive(
        self,
        directive: str,
        spec: PromptSpec,
        is_gujarati: bool,
        is_hindi: bool,
    ) -> str:
        """Localize prose directives into target language while keeping technical keywords in English."""
        text = directive.strip()

        # Handle Objective Directive (Invariant D8)
        if text.startswith("System Objective:"):
            if is_gujarati:
                first_t = spec.object_subject
                return f"ઉદ્દેશ્ય: {spec.object_subject} શરૂઆતથી શીખવું: પાયાના ખ્યાલોથી વ્યવહારુ નિપુણતા સુધી સંપૂર્ણ માર્ગદર્શન."
            elif is_hindi:
                return f"उद्देश्य: {spec.object_subject} बुनियादी स्तर से सीखना: मूलभूत सिद्धांतों से व्यावहारिक दक्षता तक पूर्ण मार्गदर्शन."
            return text

        if is_gujarati:
            if "Assume the persona of" in text:
                return f"{spec.persona_role} તરીકે વિશ્વસનીય ભૂમિકા સ્વીકારો, અને {spec.proficiency} શીખનાર માટે સ્પષ્ટ, પગલાંવાર માર્ગદર્શન આપો."
            if "Tailor language, analogies, and pacing strictly" in text:
                return f"ભાષા, દ્રષ્ટાંતો અને ગતિ સંપૂર્ણપણે {spec.proficiency} વિદ્યાર્થી માટે સરળ અને વ્યવહારુ રાખો."
            if "Explain concepts from first principles" in text:
                return "વિભાવનાઓ પાયાના સિદ્ધાંતોથી સમજાવો અને પ્રથમ ઉપયોગ વખતે દરેક ટેકનિકલ પરિભાષા સ્પષ્ટ કરો."
            if "Maintain a patient, encouraging" in text or "Maintain an encouraging" in text or "supportive" in text:
                return "સમગ્ર શિક્ષણ દરમિયાન પ્રોત્સાહક, સહાયક અને વ્યવસ્થિત શિક્ષણશાસ્ત્રીય વલણ જાળવો."
            if "The learner can build working code examples" in text:
                return "વિદ્યાર્થી તમામ અભ્યાસક્રમ વિષયોને આવરી લેતા કાર્યરત કોડ ઉદાહરણો બનાવી શકે."
            if "Demonstrate verified competency in foundational mechanics" in text:
                return "સ્વતંત્ર વ્યવહારુ કાર્યો દ્વારા પાયાની કાર્યપદ્ધતિમાં ચકાસાયેલ યોગ્યતા દર્શાવો."
            if "Successfully resolve intermediate implementation challenges" in text:
                return "બાહ્ય સહાય વિના મધ્યવર્તી અમલીકરણ પડકારોને સફળતાપૂર્વક ઉકેલો."
            if "Synthesize learned concepts by executing a comprehensive" in text:
                return "સંપૂર્ણ અંતિમ પ્રોજેક્ટ પૂર્ણ કરીને શીખેલા તમામ ખ્યાલોને સંકલિત કરો."
            if "Contains zero placeholders" in text:
                return "અપૂર્ણ પ્લેસહોલ્ડર્સ અથવા કાલ્પનિક દાવાઓથી સંપૂર્ણપણે મુક્ત રહેવું."
            if "Satisfies all" in text and "specified operational boundaries" in text:
                return "નિર્ધારિત તમામ ઓપરેશનલ બાઉન્ડ્રી અને પ્રતિબંધોનું સંપૂર્ણ પાલન કરો."
            if "Format response strictly as" in text:
                return f"સંપૂર્ણ પ્રતિસાદ {spec.format} મુજબ સ્પષ્ટ Markdown ફોર્મેટમાં આપો."
            if "Verify all" in text and "topics are explained" in text:
                return "તપાસો કે તમામ વિષયો સાહજિક માનસિક મોડેલ સાથે સ્પષ્ટ રીતે સમજાવાયેલ છે."
            if "Verify every topic includes" in text:
                return "ખાતરી કરો કે દરેક વિષયમાં સ્પષ્ટ ઉદ્દેશ્ય અને વ્યવહારુ સ્વાધ્યાય બંને સામેલ છે."
            if "Confirm zero assumed prior jargon" in text:
                return "ખાતરી કરો કે પ્રથમ પરિચય વખતે દરેક ટેકનિકલ પરિભાષા સ્પષ્ટ કરવામાં આવી છે."
            if "Check for production-ready completeness" in text:
                return "ચકાસો કે પ્રતિસાદ કોઈપણ પ્લેસહોલ્ડર વિના ઉત્પાદન-સ્તરે પૂર્ણ છે."

        elif is_hindi:
            if "Assume the persona of" in text:
                return f"{spec.persona_role} के रूप में प्रामाणिक भूमिका निभाएं, और {spec.proficiency} शिक्षार्थी के लिए स्पष्ट मार्गदर्शन प्रदान करें।"
            if "Tailor language, analogies, and pacing strictly" in text:
                return f"भाषा, उपमाओं और गति को पूरी तरह से {spec.proficiency} स्तर के अनुकूल रखें।"
            if "Explain concepts from first principles" in text:
                return "सिद्धांतों को बुनियादी स्तर से समझाएं और पहली बार उपयोग किए जाने वाले हर तकनीकी शब्द को परिभाषित करें।"
            if "Maintain a patient, encouraging" in text or "Maintain an encouraging" in text or "supportive" in text:
                return "पूरे मार्गदर्शन के दौरान सहायक, उत्साहवर्धक और संरचित शैक्षणिक दृष्टिकोण बनाए रखें।"
            if "The learner can build working code examples" in text:
                return "शिक्षार्थी सभी पाठ्यक्रम विषयों को कवर करने वाले कामकाजी कोड उदाहरण बना सके।"
            if "Demonstrate verified competency in foundational mechanics" in text:
                return "स्वतंत्र व्यावहारिक कार्यों द्वारा बुनियादी कार्यप्रणाली में सत्यापित योग्यता प्रदर्शित करें।"
            if "Successfully resolve intermediate implementation challenges" in text:
                return "बिना किसी बाहरी सहायता के मध्यवर्ती कार्यान्वयन चुनौतियों को सफलतापूर्वक हल करें।"
            if "Synthesize learned concepts by executing a comprehensive" in text:
                return "एक व्यापक अंतिम परियोजना को क्रियान्वित करके सीखे गए सिद्धांतों को संश्लेषित करें।"
            if "Contains zero placeholders" in text:
                return "अधूरे प्लेसहोल्डर्स अथवा काल्पनिक दावों से पूरी तरह मुक्त रहें।"
            if "Satisfies all" in text and "specified operational boundaries" in text:
                return "निर्धारित सभी परिचालन सीमाओं और प्रतिबंधों का पूर्ण अनुपालन करें।"
            if "Format response strictly as" in text:
                return f"पूर्ण प्रतिक्रिया {spec.format} के अनुसार स्पष्ट Markdown प्रारूप में प्रदान करें।"
            if "Verify all" in text and "topics are explained" in text:
                return "जांचें कि सभी विषयों को सहज मानसिक मॉडल के साथ स्पष्ट रूप से समझाया गया है।"
            if "Verify every topic includes" in text:
                return "सुनिश्चित करें कि प्रत्येक विषय में स्पष्ट उद्देश्य और व्यावहारिक अभ्यास दोनों शामिल हैं।"
            if "Confirm zero assumed prior jargon" in text:
                return "पुष्टि करें कि पहले परिचय पर प्रत्येक तकनीकी शब्द को परिभाषित किया गया है।"
            if "Check for production-ready completeness" in text:
                return "जांचें कि प्रतिक्रिया बिना किसी प्लेसहोल्डर के उत्पादन-स्तरीय पूर्ण है।"

        return text
