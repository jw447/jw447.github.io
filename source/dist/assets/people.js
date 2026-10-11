document.addEventListener('DOMContentLoaded', () => {
 if (!window.HTMLDialogElement || !HTMLDialogElement.prototype.showModal) return;
 document.querySelectorAll('.person-open').forEach(button => {
  const dialog = document.getElementById(button.dataset.personDialog);
  if (!dialog) return;
  button.closest('.person-card').classList.add('person-interactive');
  button.addEventListener('click', () => dialog.showModal());
  dialog.querySelector('.person-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
   const box = dialog.getBoundingClientRect();
   if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
  });
  dialog.addEventListener('close', () => button.focus());
 });
});
