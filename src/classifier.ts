// TF-IDF & Keyword Intent Classifier

import { TRAINING } from './kb.js';

function tokenize(text: string): string[] {
  return text
    .toLowerCase()
    .replace(/[^\w\s]/g, '')
    .split(/\s+/)
    .filter(Boolean);
}

class TfidfClassifier {
  private vocab: string[] = [];
  private docVectors: Map<number, number[]> = new Map();
  private docLabels: string[] = [];
  private idf: Map<string, number> = new Map();

  constructor() {
    this.train();
  }

  private train() {
    const documents = TRAINING.map(([text]) => tokenize(text));
    this.docLabels = TRAINING.map(([, label]) => label);

    // Build vocabulary
    const vocabSet = new Set<string>();
    documents.forEach((doc) => doc.forEach((term) => vocabSet.add(term)));
    this.vocab = Array.from(vocabSet);

    const N = documents.length;

    // Calculate IDF
    this.vocab.forEach((term) => {
      const docCount = documents.filter((doc) => doc.includes(term)).length;
      this.idf.set(term, Math.log((N + 1) / (docCount + 1)) + 1);
    });

    // Calculate TF-IDF vectors for training documents
    documents.forEach((doc, idx) => {
      this.docVectors.set(idx, this.vectorize(doc));
    });
  }

  private vectorize(tokens: string[]): number[] {
    const tf = new Map<string, number>();
    tokens.forEach((term) => tf.set(term, (tf.get(term) || 0) + 1));

    return this.vocab.map((term) => {
      const count = tf.get(term) || 0;
      const termFreq = tokens.length > 0 ? count / tokens.length : 0;
      const idfVal = this.idf.get(term) || 1;
      return termFreq * idfVal;
    });
  }

  private cosineSimilarity(v1: number[], v2: number[]): number {
    let dot = 0;
    let norm1 = 0;
    let norm2 = 0;
    for (let i = 0; i < v1.length; i++) {
      dot += v1[i] * v2[i];
      norm1 += v1[i] * v1[i];
      norm2 += v2[i] * v2[i];
    }
    if (norm1 === 0 || norm2 === 0) return 0;
    return dot / (Math.sqrt(norm1) * Math.sqrt(norm2));
  }

  public predict(text: string): { label: string; conf: number } {
    const tokens = tokenize(text);
    const queryVec = this.vectorize(tokens);

    let maxSim = -1;
    let bestLabel = 'general_knowledge';

    this.docVectors.forEach((docVec, idx) => {
      const sim = this.cosineSimilarity(queryVec, docVec);
      if (sim > maxSim) {
        maxSim = sim;
        bestLabel = this.docLabels[idx];
      }
    });

    return { label: bestLabel, conf: maxSim > 0 ? maxSim : 0.5 };
  }
}

const classifier = new TfidfClassifier();

export function predictIntent(text: string): { label: string; conf: number } {
  const result = classifier.predict(text);
  let label = result.label;

  const lower = text.toLowerCase();
  const medKeywords = [
    'side effect',
    'side effects',
    'can i take',
    'medication',
    'dose',
    'tell me about',
    'information about',
  ];

  if (medKeywords.some((k) => lower.includes(k))) {
    label = 'med_info';
  }

  return { label, conf: result.conf };
}
