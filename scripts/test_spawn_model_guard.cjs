'use strict';

const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const { mkdtempSync, rmSync, writeFileSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join } = require('node:path');
const { test } = require('node:test');

const guard = join(__dirname, 'spawn-model-guard.cjs');
const turn = 'current-turn';
const task = 'review_example';
const model = 'gpt-6.2-sol';
const header = 'Subagent model comparison [review_example] [gpt-6.2-sol]';
const luna = 'Model comparison [gpt-6-luna]: A task-specific requirement';
const terra = 'Model comparison [gpt-6.1-terra]: Another task-specific requirement';

function decision(overrides = {}, candidates = []) {
  const result = spawnSync(process.execPath, [guard, ...candidates], {
    encoding: 'utf8',
    input: JSON.stringify({
      hook_event_name: 'PreToolUse',
      tool_name: 'collaborationspawn_agent',
      tool_input: { task_name: task, model },
      tool_use_id: 'pending-spawn',
      turn_id: turn,
      ...overrides,
    }),
  });
  assert.equal(result.status, 0, result.stderr);
  const output = JSON.parse(result.stdout);
  if (output.hookSpecificOutput?.permissionDecision === 'deny') return 'deny';
  assert.deepEqual(output, {});
  return 'allow';
}

test('requires an explicit model and permits Luna and Terra', () => {
  assert.equal(decision({ tool_input: {} }), 'deny');
  for (const slug of ['gpt-6-luna', 'gpt-6.1-terra']) {
    assert.equal(decision({ tool_input: { model: slug } }), 'allow');
  }
  assert.equal(decision({ tool_name: 'update_plan' }), 'allow');
  assert.equal(decision(), 'deny');
});

test('binds comparison reasons to the current turn and assignment', (t) => {
  const directory = mkdtempSync(join(tmpdir(), 'ai-office-guard-'));
  t.after(() => rmSync(directory, { recursive: true, force: true }));
  const transcript = join(directory, 'session.jsonl');

  function compare(lines, turnId = turn) {
    const entries = [
      { type: 'turn_context', payload: { turn_id: turnId } },
      {
        type: 'response_item',
        payload: {
          type: 'message',
          role: 'assistant',
          phase: 'commentary',
          content: [{ type: 'output_text', text: lines.join('\n') }],
        },
      },
    ];
    writeFileSync(transcript, entries.map((entry) => JSON.stringify(entry)).join('\r\n') + '\r\n');
  }

  const evidence = { transcript_path: transcript };
  compare([header, luna, terra]);
  assert.equal(decision(evidence), 'allow');
  assert.equal(decision({ ...evidence, tool_input: { task_name: 'other_task', model } }), 'deny');

  compare([header, luna, 'Subagent model comparison [other_task] [gpt-6.2-sol]', terra]);
  assert.equal(decision(evidence), 'deny');

  compare([header, luna, terra], 'prior-turn');
  assert.equal(decision(evidence), 'deny');

  compare([header, 'Model comparison [custom-candidate]: A task-specific requirement']);
  assert.equal(decision(evidence, ['custom-candidate']), 'allow');
});
