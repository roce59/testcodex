const { execFile } = require('child_process');
const path = require('path');

function loadApps() {
  const script = path.join(__dirname, '..', 'list_apps.py');
  execFile('python', [script, '--json'], (error, stdout, stderr) => {
    if (error) {
      document.getElementById('apps').textContent = 'Error: ' + error.message;
      return;
    }
    try {
      const apps = JSON.parse(stdout);
      const ul = document.getElementById('apps');
      apps.forEach(app => {
        const li = document.createElement('li');
        li.textContent = app;
        ul.appendChild(li);
      });
    } catch (e) {
      document.getElementById('apps').textContent = 'Failed to parse output.';
    }
  });
}

document.addEventListener('DOMContentLoaded', loadApps);
