'use strict';

const fs = require('node:fs');

const candidates = process.argv.slice(2).length > 0
  ? process.argv.slice(2)
  : ['gpt-6-luna', 'gpt-6.1-terra'];

let input;
try {
  input = JSON.parse(fs.readFileSync(0, 'utf8'));
} catch {
  process.stderr.write('spawn guard: malformed JSON input\n');
  process.exit(2);
}
if (!input || typeof input !== 'object' || Array.isArray(input)) {
  process.stderr.write('spawn guard: expected a JSON object\n');
  process.exit(2);
}

const emit = (denied, reason) => {
  const output = denied
    ? { hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision: 'deny',
      permissionDecisionReason: reason,
    } }
    : {};
  process.stdout.write(JSON.stringify(output));
};
const deny = (reason) => {
  emit(true, reason);
  process.exit(0);
};
const guidance = (taskName, model, detail) => (
  `${detail}\nBefore assigning higher-cost model ${model}, add these standalone lines to the latest assistant commentary in this turn:\nSubagent model comparison [${taskName}] [${model}]\n${candidates.map((candidate) => `Model comparison [${candidate}]: <reason>`).join('\n')}`
);

if (input.hook_event_name !== 'PreToolUse' || !/(^Agent$|spawn_agent$)/.test(String(input.tool_name || ''))) {
  emit(false);
  process.exit(0);
}

const toolInput = input.tool_input && typeof input.tool_input === 'object'
  ? input.tool_input
  : {};
const model = typeof toolInput.model === 'string' ? toolInput.model.trim() : '';
if (!model) {
  deny('Specify an explicit child model in tool_input.model; child agents otherwise inherit the parent model.');
}
if (!/^gpt-\d+(?:\.\d+)?-(?:sol|astra)$/i.test(model)) {
  emit(false);
  process.exit(0);
}

const taskName = typeof toolInput.task_name === 'string' ? toolInput.task_name.trim() : '';
if (!taskName || typeof input.transcript_path !== 'string' || !input.transcript_path.trim()
    || typeof input.turn_id !== 'string' || !input.turn_id.trim()) {
  deny(guidance(taskName || '<task_name>', model, 'Provide tool_input.task_name, transcript_path, and turn_id.'));
}

let transcriptLines;
try {
  transcriptLines = fs.readFileSync(input.transcript_path, 'utf8')
    .split(/\r?\n/)
    .filter((line) => line.length > 0)
    .map((line) => JSON.parse(line));
} catch {
  deny(guidance(taskName, model, 'The current turn transcript could not be read or parsed.'));
}

let activeTurn = false;
let foundMatchingContext = false;
let latestCommentary = '';
let foundCall = false;
let superseded = false;
for (const entry of transcriptLines) {
  const payload = entry && entry.payload;
  if (entry?.type === 'turn_context') {
    if (activeTurn && payload?.turn_id !== input.turn_id) {
      activeTurn = false;
      superseded = true;
    }
    if (payload?.turn_id === input.turn_id) {
      activeTurn = true;
      foundMatchingContext = true;
      latestCommentary = '';
      superseded = false;
    }
    continue;
  }
  if (!activeTurn || entry?.type !== 'response_item' || !payload) continue;
  if (payload.type === 'function_call' && payload.call_id === input.tool_use_id) {
    foundCall = true;
    break;
  }
  if (payload.type === 'message' && payload.role === 'assistant' && payload.phase === 'commentary') {
    const parts = Array.isArray(payload.content)
      ? payload.content.filter((item) => item && typeof item.text === 'string').map((item) => item.text)
      : [];
    latestCommentary = parts.join('\n');
  }
}

if (!foundMatchingContext) {
  deny(guidance(taskName, model, 'The transcript has no matching current turn.'));
}
if (superseded && !foundCall) {
  deny(guidance(taskName, model, 'The matching turn was superseded before the spawn call was located.'));
}

const lines = latestCommentary.split(/\r?\n/);
const header = `Subagent model comparison [${taskName}] [${model}]`;
const headerIndex = lines.findIndex((line) => line.trim() === header);
const block = [];
for (const line of lines.slice(headerIndex + 1)) {
  if (line.trimStart().startsWith('Subagent model comparison [')) break;
  block.push(line);
}

const missingCandidates = candidates.filter((candidate) => {
  const prefix = `Model comparison [${candidate}]: `;
  return !block.some((line) => (
    line.startsWith(prefix) && line.slice(prefix.length).trim().length > 0
  ));
});
if (headerIndex < 0 || missingCandidates.length > 0) {
  deny(guidance(taskName, model, 'The latest commentary is missing the complete comparison block.'));
}

emit(false);
