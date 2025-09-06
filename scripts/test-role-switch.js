const assert = require('assert');
const { JSDOM } = require('jsdom');

const html = `
<div id="planner-role-menu">
  <button class="nav-btn" data-role="P">P</button>
  <button class="nav-btn" data-role="D">D</button>
  <button class="nav-btn" data-role="C">C</button>
  <button class="nav-btn" data-role="A">A</button>
</div>
<script>
var activePlannerRole = 'P';
const roleMenu = document.getElementById('planner-role-menu');
function renderSquadPlanner(){}
function setupSquadPlanner(){}
function updateBudgetUI(){}
function updateTargetsUI(){}
roleMenu.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    roleMenu.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activePlannerRole = btn.dataset.role;
    renderSquadPlanner();
    setupSquadPlanner();
    updateBudgetUI();
    updateTargetsUI();
  });
});
</script>
`;

const dom = new JSDOM(html, { runScripts: 'dangerously' });
const { document } = dom.window;

const buttons = document.querySelectorAll('.nav-btn');
buttons.forEach(btn => {
  btn.click();
  assert.strictEqual(document.querySelector('.nav-btn.active'), btn, `Button ${btn.dataset.role} should be active`);
  assert.strictEqual(dom.window.activePlannerRole, btn.dataset.role, `activePlannerRole should be ${btn.dataset.role}`);
});

console.log('Role switch test passed.');

