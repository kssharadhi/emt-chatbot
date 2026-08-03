import express, { Request, Response } from 'express';
import session from 'express-session';
import path from 'path';
import fs from 'fs';
import crypto from 'crypto';
import { fileURLToPath } from 'url';
import { FAQ } from './kb.js';
import { predictIntent } from './classifier.js';
import {
  extractSymptoms,
  runTriage,
  medicationReplyHtml,
  prettyPrintTriageHtml,
  cannedReply,
} from './triage.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.resolve(__dirname, '..');

const DATA_DIR = path.join(ROOT_DIR, 'data');
const SESSIONS_DIR = path.join(DATA_DIR, 'sessions');
const USERS_FILE = path.join(DATA_DIR, 'users.txt');
const DEBUG_LOG = path.join(DATA_DIR, 'debug.log');

// Ensure directories exist
if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
if (!fs.existsSync(SESSIONS_DIR)) fs.mkdirSync(SESSIONS_DIR, { recursive: true });
if (!fs.existsSync(USERS_FILE)) fs.writeFileSync(USERS_FILE, '', 'utf-8');
if (!fs.existsSync(DEBUG_LOG)) fs.writeFileSync(DEBUG_LOG, '', 'utf-8');

function debugLog(message: string): void {
  try {
    const line = `${new Date().toISOString()} - ${message}\n`;
    fs.appendFileSync(DEBUG_LOG, line, 'utf-8');
  } catch (err) {
    console.error('Could not write to debug log:', err);
  }
}

function hashPassword(pw: string): string {
  return crypto.createHash('sha256').update(pw, 'utf-8').digest('hex');
}

function loadUsers(): Record<string, string> {
  const users: Record<string, string> = {};
  if (fs.existsSync(USERS_FILE)) {
    const lines = fs.readFileSync(USERS_FILE, 'utf-8').split(/\r?\n/);
    for (const line of lines) {
      if (line.includes(':')) {
        const [u, h] = line.split(':', 2);
        if (u && h) {
          users[u.trim()] = h.trim();
        }
      }
    }
  }
  return users;
}

function saveUser(username: string, password: string): boolean {
  const users = loadUsers();
  if (users[username]) return false;
  const line = `${username}:${hashPassword(password)}\n`;
  fs.appendFileSync(USERS_FILE, line, 'utf-8');
  return true;
}

// Ensure default admin user
const initialUsers = loadUsers();
if (!initialUsers['admin']) {
  fs.appendFileSync(USERS_FILE, `admin:${hashPassword('admin123')}\n`, 'utf-8');
  debugLog('Created default admin user');
}

// Session logging state
const activeSessionPaths = new Map<string, string>();

function startSession(username: string): void {
  const now = new Date();
  const pad = (n: number) => String(n).padStart(2, '0');
  const ts = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(
    now.getDate()
  )}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
  const sessionPath = path.join(SESSIONS_DIR, `${username}_${ts}.jsonl`);
  activeSessionPaths.set(username, sessionPath);

  const record = JSON.stringify({
    event: 'session_start',
    user: username,
    time: now.toISOString(),
  });
  fs.appendFileSync(sessionPath, record + '\n', 'utf-8');
}

function logEvent(username: string, event: string, payload: Record<string, unknown>): void {
  let sessionPath = activeSessionPaths.get(username);
  if (!sessionPath) {
    const now = new Date();
    const pad = (n: number) => String(n).padStart(2, '0');
    const ts = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(
      now.getDate()
    )}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
    sessionPath = path.join(SESSIONS_DIR, `${username}_${ts}.jsonl`);
    activeSessionPaths.set(username, sessionPath);
  }

  const record = JSON.stringify({
    event,
    time: new Date().toISOString(),
    user: username,
    ...payload,
  });
  fs.appendFileSync(sessionPath, record + '\n', 'utf-8');
}

function getUserSessions(username: string): string[] {
  if (!fs.existsSync(SESSIONS_DIR)) return [];
  const files = fs.readdirSync(SESSIONS_DIR);
  return files
    .filter((f) => f.startsWith(`${username}_`) && f.endsWith('.jsonl'))
    .map((f) => path.join(SESSIONS_DIR, f));
}

function getSessionContent(sessionFile: string): Record<string, unknown>[] {
  const content: Record<string, unknown>[] = [];
  if (!fs.existsSync(sessionFile)) return content;
  const lines = fs.readFileSync(sessionFile, 'utf-8').split(/\r?\n/);
  for (const line of lines) {
    if (!line.trim()) continue;
    try {
      content.push(JSON.parse(line));
    } catch {
      // ignore
    }
  }
  return content;
}

function deleteUserSessions(username: string): number {
  let deleted = 0;
  const sessionFiles = getUserSessions(username);
  for (const f of sessionFiles) {
    try {
      fs.unlinkSync(f);
      deleted++;
    } catch {
      // ignore
    }
  }
  return deleted;
}

// Express App Setup
const app = express();
const PORT = 3000;

app.set('view engine', 'ejs');
app.set('views', path.join(ROOT_DIR, 'views'));

app.use(express.static(path.join(ROOT_DIR, 'public')));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use(
  session({
    secret: 'medical_chatbot_secret_key',
    resave: false,
    saveUninitialized: false,
  })
);

declare module 'express-session' {
  interface SessionData {
    username?: string;
  }
}

// Routes
app.get('/', (req: Request, res: Response) => {
  if (req.session.username) {
    return res.redirect('/chat');
  }
  res.render('login');
});

app.post('/login', (req: Request, res: Response) => {
  const username = (req.body.username || '').trim();
  const password = (req.body.password || '').trim();

  if (!username || !password) {
    return res.render('login', { error: 'Missing credentials.' });
  }

  const users = loadUsers();
  if (users[username] && users[username] === hashPassword(password)) {
    req.session.username = username;
    startSession(username);
    return res.redirect('/chat');
  } else {
    return res.render('login', { error: 'Invalid username or password.' });
  }
});

app.post('/register', (req: Request, res: Response) => {
  const username = (req.body.username || '').trim();
  const password = (req.body.password || '').trim();

  if (!username || !password) {
    return res.render('login', { error: 'Username and password required.' });
  }

  if (saveUser(username, password)) {
    return res.render('login', { success: `User ${username} registered!` });
  } else {
    return res.render('login', { error: 'Username exists.' });
  }
});

app.get('/logout', (req: Request, res: Response) => {
  req.session.destroy(() => {
    res.redirect('/');
  });
});

app.get('/chat', (req: Request, res: Response) => {
  if (!req.session.username) return res.redirect('/');
  res.render('chat', { username: req.session.username });
});

app.get('/summary', (req: Request, res: Response) => {
  if (!req.session.username) return res.redirect('/');
  const username = req.session.username;
  const sessions = getUserSessions(username);
  const allHistory: Array<{
    timestamp: unknown;
    user_message: unknown;
    bot_response: unknown;
  }> = [];

  for (const sessionFile of sessions) {
    const content = getSessionContent(sessionFile);
    for (const entry of content) {
      if (entry.event === 'message') {
        allHistory.push({
          timestamp: entry.time,
          user_message: entry.text,
          bot_response: entry.reply,
        });
      }
    }
  }

  res.render('summary', { username, history: allHistory });
});

app.post('/delete_history', (req: Request, res: Response) => {
  if (!req.session.username) return res.redirect('/');
  deleteUserSessions(req.session.username);
  res.redirect('/summary');
});

app.get('/admin', (req: Request, res: Response) => {
  if (!req.session.username || req.session.username !== 'admin') {
    return res.redirect('/');
  }

  const users = loadUsers();
  const allSessions: Array<{
    file: string;
    username: string;
    content: Record<string, unknown>[];
  }> = [];

  if (fs.existsSync(SESSIONS_DIR)) {
    const sessionFiles = fs.readdirSync(SESSIONS_DIR).filter((f) => f.endsWith('.jsonl'));
    for (const file of sessionFiles) {
      const fullPath = path.join(SESSIONS_DIR, file);
      const content = getSessionContent(fullPath);
      allSessions.push({
        file,
        username: file.split('_')[0],
        content,
      });
    }
  }

  let debugLogs: string[] = [];
  if (fs.existsSync(DEBUG_LOG)) {
    debugLogs = fs.readFileSync(DEBUG_LOG, 'utf-8').split(/\r?\n/);
  }

  res.render('admin', {
    users: Object.keys(users),
    sessions: allSessions,
    debug_logs: debugLogs,
  });
});

app.post('/send_message', (req: Request, res: Response) => {
  if (!req.session.username) {
    return res.status(401).json({ error: 'Not logged in' });
  }

  const username = req.session.username;
  const userMessage = (req.body.message || '').trim();

  if (!userMessage) {
    return res.status(400).json({ error: 'Empty message' });
  }

  const lowerUser = userMessage.toLowerCase();

  // FAQ Check
  for (const [q, a] of Object.entries(FAQ)) {
    if (lowerUser.includes(q)) {
      logEvent(username, 'faq', { q, a });
      return res.json({ response: a });
    }
  }

  let { label: intent } = predictIntent(userMessage);

  if (['hello', 'hi', 'hey'].some((w) => lowerUser.includes(w))) {
    intent = 'greeting';
  } else if (['thank', 'thanks'].some((w) => lowerUser.includes(w))) {
    intent = 'thanks';
  } else if (['bye', 'goodbye'].some((w) => lowerUser.includes(w))) {
    intent = 'goodbye';
  }

  const { symptoms, feverTemp } =
    intent === 'symptom_report' || intent === 'ask_advice' || intent === 'ask_escalation'
      ? extractSymptoms(userMessage)
      : extractSymptoms(userMessage);

  let reply = '';

  if (symptoms.length > 0) {
    intent = 'symptom_report';
    const triageResult = runTriage(symptoms, userMessage, feverTemp);
    reply = prettyPrintTriageHtml(triageResult);
  } else if (intent === 'med_info') {
    reply = medicationReplyHtml(userMessage);
  } else {
    reply = cannedReply(intent, userMessage, symptoms, {});
  }

  logEvent(username, 'message', { intent, text: userMessage, reply });
  return res.json({ response: reply });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Medical Chatbot server listening on http://0.0.0.0:${PORT}`);
  debugLog(`Server started on port ${PORT}`);
});
