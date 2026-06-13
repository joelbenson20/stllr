import { initPages } from './pages.js';
import { initForums } from './forums.js';
import { initRoom } from './rooms.js';
import { initModals } from './modals.js';
import { initStars } from './stars.js';

const STLLR_URL = '/';

const tooltipTriggerList = document.querySelectorAll(
  '[data-bs-toggle="tooltip"]',
);
const tooltipList = [...tooltipTriggerList].map(
  (tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl),
);

document.querySelectorAll('[data-bs-toggle="popover"]').forEach(
  (el) => new bootstrap.Popover(el),
);

initModals();
initStars();
initPages();
initForums();
initRoom();

