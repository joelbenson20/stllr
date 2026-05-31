import { initPages } from './pages.js';
import { initForums } from './forums.js';
import { initRoom } from './rooms.js';
import { initModals } from './modals.js';

const STLLR_URL = '/';

const tooltipTriggerList = document.querySelectorAll(
  '[data-bs-toggle="tooltip"]',
);
const tooltipList = [...tooltipTriggerList].map(
  (tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl),
);

initModals();
initPages();
initForums();
initRoom();
