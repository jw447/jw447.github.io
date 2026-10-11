document.addEventListener('DOMContentLoaded', () => {
 if (!window.HTMLDialogElement || !HTMLDialogElement.prototype.showModal) return;
 const links = [...document.querySelectorAll('.profile-controls a')].filter(a => a.textContent.trim() === 'CV');
 if (!links.length) return;
 const dialog = document.createElement('dialog');
 dialog.className = 'cv-dialog'; dialog.setAttribute('aria-labelledby', 'cv-dialog-title');
 dialog.innerHTML = '<div class="cv-dialog-header"><h2 id="cv-dialog-title">Curriculum vitae</h2><button type="button" aria-label="Close CV preview">×</button></div><iframe title="Jinzhen Wang curriculum vitae" referrerpolicy="no-referrer" allow="fullscreen"></iframe>';
 document.body.append(dialog);
 let opener;
 links.forEach(link => {
  const match = new URL(link.href).pathname.match(/^\/file\/d\/([a-zA-Z0-9_-]+)\//);
  if (!match || new URL(link.href).hostname !== 'drive.google.com') return;
  link.setAttribute('aria-haspopup', 'dialog');
  link.addEventListener('click', event => { event.preventDefault(); opener = link; dialog.querySelector('iframe').src = 'https://drive.google.com/file/d/' + match[1] + '/preview'; dialog.showModal(); });
 });
 dialog.querySelector('button').addEventListener('click', () => dialog.close());
 dialog.addEventListener('close', () => { dialog.querySelector('iframe').removeAttribute('src'); opener?.focus(); });
});
