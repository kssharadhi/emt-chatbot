// Medical Triage Logic & HTML Generators

import {
  SYMPTOM_KB,
  SYMPTOM_SYNONYMS,
  MEDICATIONS,
  SYMPTOM_OTC_SUGGESTIONS,
  REDFLAGS,
} from './kb.js';

export interface TriageResult {
  triage_level: 'EMERGENCY' | 'URGENT' | 'NON-URGENT';
  recommendation: string;
  explanation: string[];
  probable_conditions: Record<string, string[]>;
  alerts: string[];
}

export function extractSymptoms(text: string): {
  symptoms: string[];
  feverTemp: number | null;
} {
  const lower = text.toLowerCase();
  const found = new Set<string>();
  let feverTemp: number | null = null;

  const feverPatterns = [
    /\bfever (of |over |above )?(\d{1,3})\.?(\d*)\b/i,
    /\btemperature (of |over |above )?(\d{1,3})\.?(\d*)\b/i,
    /\btemp (of |over |above )?(\d{1,3})\.?(\d*)\b/i,
  ];

  for (const pattern of feverPatterns) {
    const match = lower.match(pattern);
    if (match) {
      try {
        let temp = parseFloat(match[2]);
        if (match[3]) temp += parseFloat(`0.${match[3]}`);
        feverTemp = temp;
        found.add('fever');
        break;
      } catch {
        // continue
      }
    }
  }

  for (const symptom of Object.keys(SYMPTOM_KB)) {
    if (lower.includes(symptom)) {
      found.add(symptom);
    }
    const synonyms = SYMPTOM_SYNONYMS[symptom] || [];
    for (const syn of synonyms) {
      if (lower.includes(syn)) {
        found.add(symptom);
      }
    }
  }

  // Simple string distance for fuzzy matching
  const words = lower.match(/\b\w+\b/g) || [];
  const kbKeys = Object.keys(SYMPTOM_KB);
  for (const word of words) {
    if (word.length < 4) continue;
    for (const key of kbKeys) {
      if (key.includes(word) || word.includes(key)) {
        found.add(key);
      }
    }
  }

  if (/\b(fever|temperature|hot)\b/i.test(lower) && !found.has('fever')) {
    found.add('fever');
  }

  const painMatch = lower.match(/\bpain (in|on) my (\w+)/);
  if (painMatch) {
    const region = painMatch[2];
    const mapping: Record<string, string> = {
      stomach: 'abdominal pain',
      belly: 'abdominal pain',
      back: 'back pain',
      tooth: 'tooth pain',
      leg: 'leg pain',
    };
    found.add(mapping[region] || region);
  }

  return { symptoms: Array.from(found), feverTemp };
}

export function emergencyAlert(text: string): string[] {
  const alerts: string[] = [];
  for (const [pattern, desc] of REDFLAGS) {
    if (pattern.test(text)) {
      alerts.push(desc);
    }
  }
  return alerts;
}

export function runTriage(
  symptoms: string[],
  text: string,
  feverTemp: number | null = null
): TriageResult {
  const explanation: string[] = [];

  if (feverTemp !== null) {
    if (feverTemp >= 100.0) {
      explanation.push(`High fever detected: ${feverTemp}°F`);
      const probable: Record<string, string[]> = {};
      symptoms.forEach((s) => {
        probable[s] = SYMPTOM_KB[s] || ['Symptom noted'];
      });
      return {
        triage_level: 'EMERGENCY',
        recommendation: 'Seek immediate emergency care.',
        explanation,
        probable_conditions: probable,
        alerts: [],
      };
    } else {
      explanation.push(`Low-grade fever detected: ${feverTemp}°F`);
      const probable: Record<string, string[]> = {};
      symptoms.forEach((s) => {
        probable[s] = SYMPTOM_KB[s] || ['Symptom noted'];
      });
      return {
        triage_level: 'NON-URGENT',
        recommendation: 'Rest, hydrate, and monitor symptoms.',
        explanation,
        probable_conditions: probable,
        alerts: [],
      };
    }
  }

  const alerts = emergencyAlert(text);
  if (alerts.length > 0) {
    explanation.push(`RED-FLAG triggered: ${alerts.join(', ')}`);
    const probable: Record<string, string[]> = {};
    symptoms.forEach((s) => {
      probable[s] = SYMPTOM_KB[s] || ['Symptom noted'];
    });
    return {
      triage_level: 'EMERGENCY',
      recommendation: 'Seek immediate emergency care.',
      explanation,
      probable_conditions: probable,
      alerts,
    };
  }

  const lower = text.toLowerCase();
  if (
    ['severe', 'very bad', 'worst pain', 'unbearable'].some((w) =>
      lower.includes(w)
    )
  ) {
    explanation.push('User reports severe symptoms.');
    const probable: Record<string, string[]> = {};
    symptoms.forEach((s) => {
      probable[s] = SYMPTOM_KB[s] || ['Symptom noted'];
    });
    return {
      triage_level: 'URGENT',
      recommendation: 'See urgent care.',
      explanation,
      probable_conditions: probable,
      alerts: [],
    };
  }

  const probable: Record<string, string[]> = {};
  symptoms.forEach((s) => {
    probable[s] = SYMPTOM_KB[s] || ['Symptom noted'];
  });

  if (
    symptoms.some((k) =>
      [
        'chest pain',
        'difficulty breathing',
        'bleeding',
        'severe bleeding',
        'loss of consciousness',
      ].includes(k)
    )
  ) {
    return {
      triage_level: 'URGENT',
      recommendation: 'Immediate clinical review.',
      probable_conditions: probable,
      explanation,
      alerts: [],
    };
  }

  if (
    symptoms.includes('fever') &&
    (symptoms.includes('vomiting') || symptoms.includes('diarrhea'))
  ) {
    return {
      triage_level: 'URGENT',
      recommendation: 'Arrange medical review.',
      probable_conditions: probable,
      explanation,
      alerts: [],
    };
  }

  if (symptoms.includes('chest pain') && symptoms.includes('dizziness')) {
    return {
      triage_level: 'URGENT',
      recommendation: 'Seek immediate medical attention.',
      probable_conditions: probable,
      explanation,
      alerts: [],
    };
  }

  return {
    triage_level: 'NON-URGENT',
    recommendation: 'Self-care and GP review if symptoms persist.',
    probable_conditions: probable,
    explanation,
    alerts: [],
  };
}

export function medicationReplyHtml(text: string): string {
  const lower = text.toLowerCase();
  let found: string | null = null;

  for (const med of Object.keys(MEDICATIONS)) {
    if (lower.includes(med)) {
      found = med;
      break;
    }
    const words = med.split(' ');
    if (words.every((w) => lower.includes(w))) {
      found = med;
      break;
    }
  }

  if (!found) {
    return "Tell me the medication name (e.g., 'side effects of ibuprofen').";
  }

  const info = MEDICATIONS[found];
  const seStr = info.side_effects.join(', ');

  const capitalize = (str: string) =>
    str.charAt(0).toUpperCase() + str.slice(1);

  let html = `<div class='med-card' style='border-left-color: #8e44ad;'>`;
  html += `<span class='med-title'>💊 ${capitalize(found)}</span>`;
  html += `<b>Uses:</b> ${info.uses}<br>`;
  html += `<b>Dose:</b> ${info.dose_note}<br>`;
  html += `<b>Side Effects:</b> ${seStr}<br>`;
  html += `<b>Caution:</b> ${info.cautions}</div>`;
  return html;
}

export function prettyPrintTriageHtml(triageResult: TriageResult): string {
  const lines: string[] = [];
  const symptoms = triageResult.probable_conditions || {};

  const capitalize = (str: string) =>
    str.charAt(0).toUpperCase() + str.slice(1);

  if (Object.keys(symptoms).length > 0) {
    lines.push('<strong>Symptoms noted:</strong>');
    for (const [s, conds] of Object.entries(symptoms)) {
      lines.push(`• ${capitalize(s)}: ${conds.slice(0, 2).join(', ')}`);
    }
  }

  const level = triageResult.triage_level || 'N/A';
  const alertClass =
    level === 'EMERGENCY' || level === 'URGENT' ? 'med-alert' : 'med-card';

  lines.push(`<div class='${alertClass}'>`);
  lines.push(`<span class='med-title'>TRIAGE: ${level}</span>`);
  lines.push(`${triageResult.recommendation || ''}`);

  const alerts = triageResult.alerts || [];
  if (alerts.length > 0) {
    lines.push(`<br><br><strong>⚠️ ALERT:</strong> ${alerts.join(', ')}`);
  }
  lines.push('</div>');

  const suggestedMeds = new Set<string>();
  for (const s of Object.keys(symptoms)) {
    if (SYMPTOM_OTC_SUGGESTIONS[s]) {
      for (const medKey of SYMPTOM_OTC_SUGGESTIONS[s]) {
        if (MEDICATIONS[medKey]) {
          suggestedMeds.add(medKey);
        }
      }
    }
  }

  if (suggestedMeds.size > 0) {
    lines.push(
      "<br><strong>💊 Suggested Medications:</strong><br><span style='font-size:0.8em;color:#666'>(Consult a doctor first)</span>"
    );
    for (const medKey of suggestedMeds) {
      const info = MEDICATIONS[medKey];
      const seStr = info.side_effects.join(', ');
      lines.push(`<div class='med-card'>`);
      lines.push(`<span class='med-title'>${capitalize(medKey)}</span>`);
      lines.push(`<b>Uses:</b> ${info.uses}<br>`);
      lines.push(`<b>Dose:</b> ${info.dose_note}<br>`);
      lines.push(`<b>Side Effects:</b> ${seStr}`);
      lines.push('</div>');
    }
  }

  return lines.join('');
}

export function cannedReply(
  intent: string,
  text: string,
  symptoms: string[],
  triageResult: Partial<TriageResult>
): string {
  if (intent === 'greeting') {
    const greetings = [
      'Hi! Describe your symptoms or ask advice.',
      'Hello! How can I help you?',
    ];
    return greetings[Math.floor(Math.random() * greetings.length)];
  }
  if (intent === 'thanks') return "You're welcome! Stay safe.";
  if (intent === 'goodbye') return 'Goodbye! Stay safe.';
  if (intent === 'med_info') return medicationReplyHtml(text);
  if (intent === 'symptom_report')
    return prettyPrintTriageHtml(triageResult as TriageResult);
  return "I'm a medical assistant. Please ask about symptoms, medications, or medical advice.";
}
